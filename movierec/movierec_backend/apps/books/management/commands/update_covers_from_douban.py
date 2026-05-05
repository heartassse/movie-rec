"""
Django 管理命令：从豆瓣重新爬取所有书籍的封面URL

使用方法:
    python manage.py update_covers_from_douban
    python manage.py update_covers_from_douban --limit 100
    python manage.py update_covers_from_douban --force  # 强制更新已有封面
"""
import re
import time
import random
from django.core.management.base import BaseCommand
from django.db import transaction
import requests

from apps.books.models import Book


class Command(BaseCommand):
    help = '从豆瓣重新爬取所有书籍的封面URL'
    
    def safe_write(self, msg, style=None):
        """安全输出（避免编码错误）"""
        try:
            if style:
                self.stdout.write(style(msg))
            else:
                self.stdout.write(msg)
        except UnicodeEncodeError:
            try:
                safe_msg = msg.encode('gbk', errors='replace').decode('gbk')
                if style:
                    self.stdout.write(style(safe_msg))
                else:
                    self.stdout.write(safe_msg)
            except:
                safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
                if style:
                    self.stdout.write(style(safe_msg))
                else:
                    self.stdout.write(safe_msg)

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='只处理前N本书'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新已有封面的书籍'
        )
        parser.add_argument(
            '--delay',
            type=float,
            nargs=2,
            default=[1.5, 3.0],
            help='请求延迟范围（秒），默认：1.5 3.0'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=15,
            help='请求超时时间（秒），默认：15'
        )
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='遇到错误时跳过继续处理'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        force = options['force']
        delay_min, delay_max = options['delay']
        timeout = options['timeout']
        skip_errors = options['skip_errors']

        # 查询需要更新的书籍
        if force:
            qs = Book.objects.all()
        else:
            # 只更新没有封面的书籍
            qs = Book.objects.filter(cover_url__isnull=True) | Book.objects.filter(cover_url='')
        
        qs = qs.order_by('id')
        
        if limit:
            qs = qs[:limit]

        if not qs.exists():
            self.safe_write('没有需要更新封面的书籍', self.style.WARNING)
            return

        total = qs.count()
        self.safe_write(f'开始处理 {total} 本书籍', self.style.SUCCESS)
        self.safe_write(f'延迟范围: {delay_min}-{delay_max} 秒')
        self.safe_write(f'超时时间: {timeout} 秒')
        if not force:
            self.safe_write('模式: 仅更新没有封面的书籍')
        else:
            self.safe_write('模式: 强制更新所有书籍封面')
        self.safe_write('='*60)

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        })

        stats = {
            'total': total,
            'updated': 0,
            'not_found': 0,
            'errors': 0,
            'skipped': 0,
        }

        for idx, book in enumerate(qs, 1):
            self.safe_write(f'\n[{idx}/{total}] 处理: {book.title} (ID: {book.id})')
            
            try:
                # 使用搜索API获取封面
                cover_url = self._get_cover_from_douban(session, book.title, timeout)
                
                if not cover_url:
                    self.safe_write(f'  未找到封面', self.style.WARNING)
                    stats['not_found'] += 1
                    time.sleep(random.uniform(delay_min, delay_max))
                    continue

                # 更新数据库
                old_cover = book.cover_url
                book.cover_url = cover_url
                book.save(update_fields=['cover_url'])
                
                if old_cover:
                    self.safe_write(f'  已更新封面（替换旧封面）', self.style.SUCCESS)
                else:
                    self.safe_write(f'  已添加封面', self.style.SUCCESS)
                self.safe_write(f'  URL: {cover_url[:80]}...' if len(cover_url) > 80 else f'  URL: {cover_url}')
                stats['updated'] += 1

                # 延迟
                time.sleep(random.uniform(delay_min, delay_max))

            except Exception as e:
                self.safe_write(f'  错误: {str(e)}', self.style.ERROR)
                stats['errors'] += 1
                if not skip_errors:
                    self.safe_write('中断执行（使用 --skip-errors 可跳过错误继续）', self.style.ERROR)
                    break
                time.sleep(random.uniform(delay_min, delay_max))

        # 统计
        self.safe_write('\n' + '='*60)
        self.safe_write('完成！', self.style.SUCCESS)
        self.safe_write(f'总计: {stats["total"]} 本')
        self.safe_write(f'已更新: {stats["updated"]} 本')
        self.safe_write(f'未找到: {stats["not_found"]} 本')
        self.safe_write(f'跳过: {stats["skipped"]} 本')
        self.safe_write(f'错误: {stats["errors"]} 本')

    def _clean_title_variants(self, title):
        """生成多个书名变体用于搜索（尽可能多的尝试）"""
        variants = []
        
        # 1. 原始书名
        original = title.strip()
        variants.append(original)
        
        # 2. 移除所有括号内容（中英文）
        no_brackets = re.sub(r'[（(【\[].*?[）)\】\]]', '', title)
        no_brackets = no_brackets.strip()
        if no_brackets and no_brackets != original and len(no_brackets) >= 2:
            variants.append(no_brackets)
        
        # 3. 移除冒号/破折号后的所有内容
        for sep in ['：', ':', '—', '－', '-', '·', '、']:
            if sep in title:
                parts = title.split(sep)
                main = parts[0].strip()
                if main and len(main) >= 2 and main not in variants:
                    variants.append(main)
        
        # 4. 移除常见后缀词
        suffixes = [
            r'全.{1,3}册', r'上下册', r'[上中下]册', 
            r'增订本', r'修订版', r'珍藏版', r'典藏版', r'精装版',
            r'第.{1,2}版', r'纪念版', r'插图版', r'图文版',
        ]
        for suffix_pattern in suffixes:
            cleaned = re.sub(suffix_pattern, '', title)
            cleaned = re.sub(r'[（(【\[].*?[）)\】\]]', '', cleaned)
            cleaned = cleaned.strip()
            if cleaned and cleaned not in variants and len(cleaned) >= 2:
                variants.append(cleaned)
        
        # 5. 提取前N个字符（多个长度）
        for length in [10, 8, 6, 5, 4]:
            if len(title) > length:
                short = title[:length].strip()
                # 移除末尾的标点符号
                short = re.sub(r'[，。、：；！？·\-—－\s]+$', '', short)
                if short and len(short) >= 2 and short not in variants:
                    variants.append(short)
        
        # 6. 移除所有标点符号和空格
        no_punct = re.sub(r'[^\w\u4e00-\u9fff]', '', title)
        if no_punct and no_punct not in variants and len(no_punct) >= 2:
            variants.append(no_punct)
        
        return variants

    def _get_cover_from_douban(self, session, title, timeout):
        """从豆瓣搜索API获取封面URL（使用第一个搜索结果，不管是否匹配）"""
        
        search_variants = self._clean_title_variants(title)
        
        for idx, search_title in enumerate(search_variants):
            try:
                api_url = f'https://book.douban.com/j/subject_suggest?q={requests.utils.quote(search_title)}'
                resp = session.get(api_url, timeout=timeout)
                
                if resp.status_code in (403, 418):
                    if idx == 0:  # 只在第一次尝试时提示
                        self.safe_write(f'  被豆瓣拦截 (403/418)', self.style.WARNING)
                    return None
                
                resp.raise_for_status()
                data = resp.json()
                
                # 只要API返回任何结果，直接用第一个的封面（不管书名是否匹配）
                if isinstance(data, list) and len(data) > 0:
                    first_result = data[0]
                    cover_url = first_result.get('pic', '').strip()
                    
                    if cover_url:
                        matched_title = first_result.get('title', 'N/A')
                        if idx > 0:
                            self.safe_write(f'  用"{search_title}"搜到: {matched_title}')
                        else:
                            self.safe_write(f'  搜到: {matched_title}')
                        return cover_url
                
                # 这个变体没找到，继续尝试下一个
                
            except Exception as e:
                # 只在最后一次尝试失败时报错
                if idx == len(search_variants) - 1:
                    self.safe_write(f'  所有搜索尝试均失败', self.style.WARNING)
                continue
        
        return None
