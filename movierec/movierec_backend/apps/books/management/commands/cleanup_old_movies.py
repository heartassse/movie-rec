"""
清理旧书籍数据，只保留豆瓣电影数据集导入的电影。

豆瓣导入的电影 isbn 字段存储的是纯数字的 MOVIE_ID（如 1292052），
而旧书籍数据的 isbn 通常是 ISBN-13 格式（如 9787020002207）或为空。

使用方法：
    python manage.py cleanup_old_movies          # 预览将被删除的数据
    python manage.py cleanup_old_movies --confirm # 确认执行删除
"""

from django.core.management.base import BaseCommand
from apps.books.models import Book
from apps.ratings.models import Rating, Comment


class Command(BaseCommand):
    help = '清理旧书籍数据，只保留豆瓣电影数据集导入的电影'

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', help='确认执行删除操作')

    def handle(self, *args, **options):
        confirm = options['confirm']

        total_books = Book.objects.count()
        self.stdout.write(f'数据库中共有 {total_books} 条记录')

        douban_books = Book.objects.filter(isbn__isnull=False).exclude(isbn='')
        douban_ids = []
        old_ids = []

        for b in Book.objects.all().values_list('id', 'isbn', 'title'):
            book_id, isbn, title = b
            is_douban = False
            if isbn:
                clean_isbn = isbn.strip()
                if clean_isbn.isdigit() and len(clean_isbn) <= 10:
                    is_douban = True

            if is_douban:
                douban_ids.append(book_id)
            else:
                old_ids.append(book_id)

        self.stdout.write(f'  豆瓣电影数据: {len(douban_ids)} 条')
        self.stdout.write(f'  旧书籍数据:   {len(old_ids)} 条')

        if not old_ids:
            self.stdout.write(self.style.SUCCESS('没有需要清理的旧数据'))
            return

        old_ratings = Rating.objects.filter(book_id__in=old_ids).count()
        old_comments = Comment.objects.filter(book_id__in=old_ids).count()
        self.stdout.write(f'  关联旧评分:   {old_ratings} 条')
        self.stdout.write(f'  关联旧评论:   {old_comments} 条')

        sample = Book.objects.filter(id__in=old_ids[:5]).values_list('title', flat=True)
        self.stdout.write(f'  示例旧书籍:   {", ".join(sample)}')

        if not confirm:
            self.stdout.write(self.style.WARNING(
                '\n这是预览模式。要执行删除，请加上 --confirm 参数：\n'
                '  python manage.py cleanup_old_movies --confirm'
            ))
            return

        self.stdout.write('正在删除旧数据...')
        Rating.objects.filter(book_id__in=old_ids).delete()
        Comment.objects.filter(book_id__in=old_ids).delete()
        deleted_count = Book.objects.filter(id__in=old_ids).delete()[0]

        remaining = Book.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'清理完成！删除了 {deleted_count} 条旧记录，'
            f'剩余 {remaining} 部电影'
        ))
