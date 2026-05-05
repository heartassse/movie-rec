"""
推荐算法评估命令

评估指标：
1. Precision@K：推荐列表中用户实际喜欢的比例
2. Recall@K：用户喜欢的物品中被推荐出来的比例
3. Coverage：推荐系统能够推荐的物品占总物品的比例
4. Diversity：推荐列表的多样性
"""

from django.core.management.base import BaseCommand
from apps.ratings.models import Rating
from apps.books.models import Book
from apps.recommend.algorithms import UserCF, ItemCF
import random
from collections import defaultdict


class Command(BaseCommand):
    help = '评估推荐算法性能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--method',
            type=str,
            default='usercf',
            help='推荐算法：usercf 或 itemcf'
        )
        parser.add_argument(
            '--similarity',
            type=str,
            default='cosine',
            help='相似度计算方法：cosine 或 pearson'
        )
        parser.add_argument(
            '--k',
            type=int,
            default=10,
            help='推荐列表长度'
        )
        parser.add_argument(
            '--test-ratio',
            type=float,
            default=0.2,
            help='测试集比例'
        )
        parser.add_argument(
            '--min-ratings',
            type=int,
            default=5,
            help='用户最少评分数'
        )

    def handle(self, *args, **options):
        method = options['method']
        similarity = options['similarity']
        k = options['k']
        test_ratio = options['test_ratio']
        min_ratings = options['min_ratings']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('推荐算法评估'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'算法: {method.upper()}')
        self.stdout.write(f'相似度: {similarity}')
        self.stdout.write(f'推荐数量: Top-{k}')
        self.stdout.write(f'测试集比例: {test_ratio * 100}%')
        self.stdout.write(f'最少评分数: {min_ratings}')
        self.stdout.write('')

        # 1. 加载数据
        self.stdout.write('正在加载评分数据...')
        all_ratings = list(Rating.objects.values('user_id', 'book_id', 'score'))
        
        if not all_ratings:
            self.stdout.write(self.style.ERROR('错误：数据库中没有评分数据！'))
            return

        self.stdout.write(f'总评分数: {len(all_ratings)}')

        # 2. 筛选活跃用户
        user_rating_counts = defaultdict(int)
        for r in all_ratings:
            user_rating_counts[r['user_id']] += 1

        active_users = [uid for uid, count in user_rating_counts.items() if count >= min_ratings]
        self.stdout.write(f'活跃用户数（评分≥{min_ratings}）: {len(active_users)}')

        if len(active_users) < 10:
            self.stdout.write(self.style.WARNING('警告：活跃用户太少，评估结果可能不准确'))

        # 3. 划分训练集和测试集
        self.stdout.write('\n正在划分训练集和测试集...')
        train_data = []
        test_data = defaultdict(list)

        for user_id in active_users:
            user_ratings = [r for r in all_ratings if r['user_id'] == user_id]
            random.shuffle(user_ratings)
            
            split_point = int(len(user_ratings) * (1 - test_ratio))
            train_ratings = user_ratings[:split_point]
            test_ratings = user_ratings[split_point:]

            train_data.extend(train_ratings)
            if test_ratings:
                test_data[user_id] = test_ratings

        self.stdout.write(f'训练集大小: {len(train_data)}')
        self.stdout.write(f'测试用户数: {len(test_data)}')

        # 4. 训练模型
        self.stdout.write('\n正在训练推荐模型...')
        
        if method == 'usercf':
            model = UserCF(
                similarity_method=similarity,
                normalize=True,
                k_neighbors=30,
                min_common_items=3
            )
        else:  # itemcf
            model = ItemCF(
                similarity_method=similarity,
                use_adjusted=True,
                k_neighbors=20,
                min_common_users=3
            )

        model.fit([
            {'user_id': r['user_id'], 'item_id': r['book_id'], 'score': r['score']}
            for r in train_data
        ])

        self.stdout.write(self.style.SUCCESS('模型训练完成！'))

        # 5. 生成推荐并评估
        self.stdout.write('\n正在生成推荐并评估...')
        
        precision_list = []
        recall_list = []
        recommended_items = set()
        total_items = Book.objects.count()

        for user_id, test_ratings in test_data.items():
            # 获取用户在训练集中的评分
            user_train_ratings = {
                r['book_id']: float(r['score']) 
                for r in train_data if r['user_id'] == user_id
            }

            if not user_train_ratings:
                continue

            # 生成推荐
            if method == 'usercf':
                recommendations = model.recommend(user_id, top_n=k)
            else:  # itemcf
                recommendations = model.recommend(user_id, user_train_ratings, top_n=k)

            if not recommendations:
                continue

            rec_items = set(item_id for item_id, _ in recommendations)
            recommended_items.update(rec_items)

            # 测试集中用户喜欢的物品（评分>=4）
            liked_items = set(r['book_id'] for r in test_ratings if r['score'] >= 4)

            if not liked_items:
                continue

            # 计算Precision和Recall
            hit = len(rec_items & liked_items)
            precision = hit / len(rec_items) if rec_items else 0
            recall = hit / len(liked_items) if liked_items else 0

            precision_list.append(precision)
            recall_list.append(recall)

        # 6. 输出评估结果
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('评估结果'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        if precision_list:
            avg_precision = sum(precision_list) / len(precision_list)
            avg_recall = sum(recall_list) / len(recall_list)
            coverage = len(recommended_items) / total_items if total_items > 0 else 0
            
            # F1-Score
            if avg_precision + avg_recall > 0:
                f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
            else:
                f1_score = 0

            self.stdout.write(f'Precision@{k}: {avg_precision:.4f} ({avg_precision*100:.2f}%)')
            self.stdout.write(f'Recall@{k}: {avg_recall:.4f} ({avg_recall*100:.2f}%)')
            self.stdout.write(f'F1-Score: {f1_score:.4f}')
            self.stdout.write(f'Coverage: {coverage:.4f} ({coverage*100:.2f}%)')
            self.stdout.write(f'推荐物品数: {len(recommended_items)} / {total_items}')
            self.stdout.write(f'评估用户数: {len(precision_list)}')
        else:
            self.stdout.write(self.style.ERROR('错误：无法生成有效的推荐结果'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('评估完成！'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
