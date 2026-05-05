"""
Django 管理命令：为评论随机生成发布时间

使用方法:
    python manage.py randomize_comment_dates
    python manage.py randomize_comment_dates --days 365  # 指定时间范围（天数）
    python manage.py randomize_comment_dates --limit 1000  # 只处理前N条
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from apps.ratings.models import Comment


class Command(BaseCommand):
    help = '为评论随机生成发布时间（用于演示和测试）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=730,
            help='时间范围：过去N天内（默认730天，约2年）'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='只处理前N条评论'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='批次大小（默认500）'
        )

    def handle(self, *args, **options):
        days = options['days']
        limit = options['limit']
        batch_size = options['batch_size']

        now = timezone.now()
        start_time = now - timedelta(days=days)

        qs = Comment.objects.all().order_by('id')
        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('没有找到评论数据'))
            return

        self.stdout.write(self.style.SUCCESS(f'开始处理 {total} 条评论'))
        self.stdout.write(f'时间范围: {start_time.strftime("%Y-%m-%d")} 至 {now.strftime("%Y-%m-%d")}')
        self.stdout.write('='*60)

        updated = 0
        comments_to_update = []

        for idx, comment in enumerate(qs.iterator(chunk_size=batch_size), 1):
            # 生成随机时间
            random_seconds = random.randint(0, days * 24 * 3600)
            random_time = start_time + timedelta(seconds=random_seconds)
            
            comment.created_at = random_time
            comments_to_update.append(comment)

            # 批量更新
            if len(comments_to_update) >= batch_size:
                Comment.objects.bulk_update(comments_to_update, ['created_at'])
                updated += len(comments_to_update)
                self.stdout.write(f'已更新 {updated}/{total} 条评论...')
                comments_to_update = []

        # 处理剩余的
        if comments_to_update:
            Comment.objects.bulk_update(comments_to_update, ['created_at'])
            updated += len(comments_to_update)

        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS(f'完成！共更新 {updated} 条评论的发布时间'))
