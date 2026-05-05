"""
Django管理命令：列出所有电影
使用方法: python manage.py list_movies
"""
from django.core.management.base import BaseCommand
from apps.books.models import Book
from datetime import datetime
import os


class Command(BaseCommand):
    help = '列出数据库中保存的所有书籍名称'

    def add_arguments(self, parser):
        parser.add_argument(
            '--simple',
            action='store_true',
            help='仅显示书名（简化输出）',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=None,
            help='限制显示的数量',
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help='导出到txt文件（指定文件路径）',
        )

    def handle(self, *args, **options):
        books = Book.objects.all().order_by('title')
        total_count = books.count()
        
        if options['count']:
            books = books[:options['count']]
        
        # 如果指定了输出文件，导出到文件
        if options['output']:
            output_file = options['output']
            self._export_to_file(books, total_count, output_file, options['simple'])
            return
        
        if options['simple']:
            # 简化输出：仅显示书名
            self.stdout.write(f"\n共 {total_count} 本书籍（显示前 {len(books)} 本）：\n")
            for idx, book in enumerate(books, 1):
                self.stdout.write(f"{idx}. {book.title}")
        else:
            # 详细输出：显示书名、作者、ISBN
            self.stdout.write("=" * 80)
            self.stdout.write(f"数据库中总共有 {total_count} 本书籍")
            if options['count']:
                self.stdout.write(f"（显示前 {len(books)} 本）")
            self.stdout.write("=" * 80)
            self.stdout.write("")
            
            for idx, book in enumerate(books, 1):
                author_info = f" - {book.author[:40]}" if book.author else ""
                isbn_info = f" [ISBN: {book.isbn}]" if book.isbn else ""
                cover_info = " [有封面]" if book.cover_url else " [无封面]"
                self.stdout.write(f"{idx:5d}. {book.title}{author_info}{isbn_info}{cover_info}")
            
            self.stdout.write("")
            self.stdout.write("=" * 80)
            self.stdout.write(f"共 {total_count} 本书籍")
            self.stdout.write("=" * 80)
        
        self.stdout.write("")
    
    def _export_to_file(self, books, total_count, output_file, simple=False):
        """导出书籍列表到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"书籍列表\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总书籍数: {total_count}\n")
                f.write("=" * 80 + "\n\n")
                
                if simple:
                    # 简化输出：仅书名
                    for idx, book in enumerate(books, 1):
                        f.write(f"{idx}. {book.title}\n")
                else:
                    # 详细输出
                    for idx, book in enumerate(books, 1):
                        author_info = f" - {book.author[:40]}" if book.author else ""
                        isbn_info = f" [ISBN: {book.isbn}]" if book.isbn else ""
                        cover_info = " [有封面]" if book.cover_url else " [无封面]"
                        f.write(f"{idx:5d}. {book.title}{author_info}{isbn_info}{cover_info}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"共 {total_count} 本书籍\n")
                f.write("=" * 80 + "\n")
            
            file_size = os.path.getsize(output_file) / 1024
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ 成功导出 {len(books)} 本书籍到文件: {output_file}'
            ))
            self.stdout.write(f'文件大小: {file_size:.2f} KB')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导出失败: {e}'))
