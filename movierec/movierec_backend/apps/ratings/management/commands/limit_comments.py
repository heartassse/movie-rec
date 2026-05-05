"""
Django 管理命令：限制每本书的评论数量

使用方法:
    python manage.py limit_comments --min 10 --max 20
    python manage.py limit_comments --min 10 --max 20 --dry-run  # 预览模式，不实际删除
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
import random

from apps.books.models import Book
from apps.ratings.models import Comment


class Command(BaseCommand):
    help = '限制每本书的评论数量，删除多余的评论'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min',
            type=int,
            default=10,
            help='每本书最少保留的评论数量（默认：10）'
        )
        parser.add_argument(
            '--max',
            type=int,
            default=20,
            help='每本书最多保留的评论数量（默认：20）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式：只显示将要删除的评论，不实际删除'
        )

    def handle(self, *args, **options):
        min_count = options.get('min', 10)
        max_count = options.get('max', 20)
        dry_run = options.get('dry_run', False)

        if min_count < 0 or max_count < 0:
            self.stdout.write(self.style.ERROR('评论数量不能为负数'))
            return

        if min_count > max_count:
            self.stdout.write(self.style.ERROR('最少数量不能大于最多数量'))
            return

        self.stdout.write(self.style.SUCCESS('开始处理评论限制...'))
        self.stdout.write(f'每本书保留评论数量: {min_count} - {max_count} 条')
        if dry_run:
            self.stdout.write(self.style.WARNING('预览模式：不会实际删除数据'))
        self.stdout.write('='*60)

        stats = {
            'books_processed': 0,
            'books_with_excess': 0,
            'comments_deleted': 0,
            'comments_kept': 0,
        }

        # 获取所有有评论的书籍
        books_with_comments = Book.objects.annotate(
            comment_count=Count('comments')
        ).filter(comment_count__gt=0).order_by('id')

        total_books = books_with_comments.count()
        self.stdout.write(f'找到 {total_books} 本有评论的书籍')

        for book in books_with_comments:
            stats['books_processed'] += 1
            comment_count = book.comment_count

            # 如果评论数量在范围内，跳过
            if min_count <= comment_count <= max_count:
                stats['comments_kept'] += comment_count
                continue

            # 获取该书籍的所有评论
            comments = Comment.objects.filter(book=book).order_by('-created_at')

            if comment_count > max_count:
                # 评论数量超过最大值，需要删除多余的
                stats['books_with_excess'] += 1
                
                # 随机选择保留的数量（在 min 和 max 之间）
                keep_count = random.randint(min_count, max_count)
                
                # 保留最新的 keep_count 条评论（按创建时间降序）
                # 获取要保留的评论 ID
                comments_to_keep_ids = list(comments[:keep_count].values_list('id', flat=True))
                # 获取要删除的评论 ID
                comments_to_delete_ids = list(comments[keep_count:].values_list('id', flat=True))
                delete_count = len(comments_to_delete_ids)

                if dry_run:
                    self.stdout.write(
                        f'书籍 "{book.title}" (ID: {book.id}): '
                        f'共有 {comment_count} 条评论，将保留 {keep_count} 条，删除 {delete_count} 条'
                    )
                else:
                    # 实际删除（使用 ID 列表删除，避免 limit/offset 问题）
                    if comments_to_delete_ids:
                        Comment.objects.filter(id__in=comments_to_delete_ids).delete()
                        stats['comments_deleted'] += delete_count
                    stats['comments_kept'] += keep_count
                    
                    if stats['books_processed'] % 100 == 0:
                        self.stdout.write(
                            f'已处理 {stats["books_processed"]}/{total_books} 本书... '
                            f'已删除 {stats["comments_deleted"]} 条评论'
                        )

            elif comment_count < min_count:
                # 评论数量少于最小值，保留所有（不删除）
                stats['comments_kept'] += comment_count
                if dry_run:
                    self.stdout.write(
                        f'书籍 "{book.title}" (ID: {book.id}): '
                        f'共有 {comment_count} 条评论（少于最小值 {min_count}），全部保留'
                    )

        # 打印统计信息
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING('预览模式统计（未实际删除）:'))
        else:
            self.stdout.write(self.style.SUCCESS('处理完成！统计信息:'))
        self.stdout.write('='*60)
        self.stdout.write(f'处理的书籍数: {stats["books_processed"]}')
        self.stdout.write(f'有超出评论的书籍: {stats["books_with_excess"]}')
        self.stdout.write(f'保留的评论数: {stats["comments_kept"]}')
        if not dry_run:
            self.stdout.write(f'删除的评论数: {stats["comments_deleted"]}')
        self.stdout.write('='*60)

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n这是预览模式，没有实际删除数据。'
            ))
            self.stdout.write(self.style.WARNING(
                '要实际执行删除，请运行相同的命令但不加 --dry-run 参数。'
            ))
