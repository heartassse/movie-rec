"""
Django 管理命令：根据数据库中的电影名去豆瓣爬取完整信息并更新

使用方法:
    python manage.py enrich_movies_from_douban
    python manage.py enrich_movies_from_douban --limit 100  # 只处理前100部
    python manage.py enrich_movies_from_douban --only-missing  # 只更新缺失字段的电影
    python manage.py enrich_movies_from_douban --delay 2 5  # 设置延迟范围（秒）
"""
import re
import time
import random
from django.core.management.base import BaseCommand
from django.db import transaction
import requests
from bs4 import BeautifulSoup

from apps.books.models import Book


class Command(BaseCommand):
    help = '根据书名从豆瓣爬取书籍详细信息并更新数据库'
    
    def safe_write(self, msg, style=None):
        """安全输出（避免编码错误）"""
        try:
            if style:
                self.stdout.write(style(msg))
            else:
                self.stdout.write(msg)
        except UnicodeEncodeError:
            # Windows GBK编码问题：替换无法编码的字符为 ?
            try:
                safe_msg = msg.encode('gbk', errors='replace').decode('gbk')
                if style:
                    self.stdout.write(style(safe_msg))
                else:
                    self.stdout.write(safe_msg)
            except:
                # 最后的备选方案：只保留ASCII字符
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
            '--only-missing',
            action='store_true',
            help='只更新缺失关键字段的书籍（作者、ISBN、封面、简介都为空）'
        )
        parser.add_argument(
            '--delay',
            nargs=2,
            type=float,
            default=[1.5, 3.0],
            help='请求延迟范围（秒），默认 1.5-3.0'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=15,
            help='请求超时时间（秒），默认15'
        )
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='遇到错误时跳过继续，而不是中断'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        only_missing = options['only_missing']
        delay_min, delay_max = options['delay']
        timeout = options['timeout']
        skip_errors = options['skip_errors']

        # 查询需要更新的书籍
        qs = Book.objects.all().order_by('id')
        
        if only_missing:
            qs = qs.filter(
                author='',
                isbn__isnull=True,
                cover_url__isnull=True,
                description__in=['', None]
            )
        
        if limit:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('没有需要更新的书籍'))
            return

        self.safe_write(f'开始处理 {total} 本书籍', self.style.SUCCESS)
        self.safe_write(f'延迟范围: {delay_min}-{delay_max} 秒')
        self.safe_write(f'超时时间: {timeout} 秒')
        if only_missing:
            self.safe_write('模式: 仅更新缺失字段的书籍')
        self.safe_write('='*60)

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
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
                # 使用API搜索（更快，直接返回基本信息）
                book_info = self._search_book_api(session, book.title, timeout)
                
                if not book_info:
                    self.safe_write(f'  未找到匹配结果', self.style.WARNING)
                    stats['not_found'] += 1
                    time.sleep(random.uniform(delay_min, delay_max))
                    continue

                self.safe_write(f'  找到: {book_info.get("url", "N/A")}')
                
                # 如果需要ISBN和详细简介，才访问详情页
                need_isbn = not book.isbn
                need_description = not book.description
                
                if (need_isbn or need_description) and book_info.get('url'):
                    self.safe_write(f'  需要详情页信息，访问: {book_info["url"]}')
                    detail_info = self._parse_book_detail(session, book_info['url'], timeout)
                    if detail_info:
                        # 合并详情信息（优先使用详情页的信息）
                        if detail_info.get('isbn'):
                            book_info['isbn'] = detail_info['isbn']
                        if detail_info.get('description'):
                            book_info['description'] = detail_info['description']
                        # 如果API没有返回作者/年份，使用详情页的
                        if not book_info.get('author') and detail_info.get('author'):
                            book_info['author'] = detail_info['author']
                        if not book_info.get('publication_year') and detail_info.get('publication_year'):
                            book_info['publication_year'] = detail_info['publication_year']

                # 更新数据库
                updated_fields = []
                if book_info.get('author') and not book.author:
                    book.author = book_info['author']
                    updated_fields.append('author')
                
                if book_info.get('publication_year') and not book.publication_year:
                    book.publication_year = book_info['publication_year']
                    updated_fields.append('publication_year')
                
                if book_info.get('isbn') and not book.isbn:
                    # 检查ISBN是否已被其他书籍使用
                    isbn_exists = Book.objects.filter(isbn=book_info['isbn']).exclude(id=book.id).exists()
                    if not isbn_exists:
                        book.isbn = book_info['isbn']
                        updated_fields.append('isbn')
                    else:
                        self.safe_write(f'  警告: ISBN {book_info["isbn"]} 已被其他书籍使用，跳过', self.style.WARNING)
                
                if book_info.get('cover_url') and not book.cover_url:
                    book.cover_url = book_info['cover_url']
                    updated_fields.append('cover_url')
                
                if book_info.get('description') and not book.description:
                    book.description = book_info['description']
                    updated_fields.append('description')

                if updated_fields:
                    book.save(update_fields=updated_fields)
                    self.safe_write(f'  已更新: {", ".join(updated_fields)}', self.style.SUCCESS)
                    stats['updated'] += 1
                else:
                    self.safe_write(f'  无需更新（字段已完整）')
                    stats['skipped'] += 1

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

    def _clean_title(self, title):
        """清理书名，提高搜索成功率
        
        返回多个可能的搜索词，按优先级排序
        """
        variants = []
        
        # 1. 原始书名
        variants.append(title.strip())
        
        # 2. 移除括号内容（包括中英文括号）
        cleaned = re.sub(r'[（(].*?[）)]', '', title)
        cleaned = cleaned.strip()
        if cleaned and cleaned != title and len(cleaned) >= 2:
            variants.append(cleaned)
        
        # 3. 移除常见分隔符后的内容
        for sep in ['：', ':', '—', '－', '-', '·', '.']:
            if sep in title:
                parts = title.split(sep)
                main_part = parts[0].strip()
                if main_part and len(main_part) >= 2 and main_part not in variants:
                    variants.append(main_part)
        
        # 4. 移除"全X册"、"上下册"等
        cleaned = re.sub(r'(全.{1,2}册|上下册|增订本|修订版|珍藏版|典藏版)', '', title)
        cleaned = cleaned.strip()
        if cleaned and cleaned not in variants and len(cleaned) >= 2:
            variants.append(cleaned)
        
        # 5. 只保留前面的主要词（如果书名很长）
        if len(title) > 10:
            short = title[:8].strip()
            if short not in variants and len(short) >= 2:
                variants.append(short)
        
        return variants
    
    def _search_book_api(self, session, title, timeout):
        """使用豆瓣搜索建议API获取书籍基本信息（更快，不需要访问详情页）
        
        返回: dict 包含 author, year, cover_url, description(无), url
        """
        # 尝试多种书名格式
        search_titles = self._clean_title(title)
        
        for idx, search_title in enumerate(search_titles):
            try:
                api_url = f'https://book.douban.com/j/subject_suggest?q={requests.utils.quote(search_title)}'
                resp = session.get(api_url, timeout=timeout)
                
                if resp.status_code in (403, 418):
                    self.safe_write(f'  被豆瓣拦截 (403/418)', self.style.WARNING)
                    return None
                
                resp.raise_for_status()
                data = resp.json()
                
                # API 返回格式: [{"title": "...", "url": "...", "author_name": "...", "year": "...", "pic": "...", "id": "..."}, ...]
                if isinstance(data, list) and len(data) > 0:
                    first_result = data[0]
                    
                    # 从API直接获取信息
                    info = {
                        'author': first_result.get('author_name', '').strip(),
                        'publication_year': None,
                        'cover_url': first_result.get('pic', '').strip(),
                        'isbn': '',  # API不返回ISBN
                        'description': '',  # API不返回简介
                        'url': first_result.get('url', '').split('?')[0].rstrip('/'),
                    }
                    
                    # 解析年份
                    year_str = first_result.get('year', '').strip()
                    if year_str and year_str.isdigit():
                        info['publication_year'] = int(year_str)
                    
                    # 如果不是用原始书名找到的，记录一下
                    if idx > 0:
                        self.safe_write(f'  （使用简化书名"{search_title}"找到）')
                    
                    return info
                
                # 如果这个书名没找到，尝试下一个
                
            except Exception as e:
                if idx == len(search_titles) - 1:
                    self.safe_write(f'  API搜索失败: {str(e)}', self.style.WARNING)
        
        return None

    def _parse_book_detail(self, session, book_url, timeout):
        """解析书籍详情页"""
        try:
            resp = session.get(book_url, timeout=timeout)
            
            if resp.status_code in (403, 418):
                return None
            
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 封面
            cover_url = ''
            cover = soup.select_one('#mainpic img')
            if cover and cover.get('src'):
                cover_url = cover.get('src')

            # 简介
            description = ''
            intro_el = soup.select_one('#link-report .intro')
            if intro_el:
                # 移除"展开全部"等链接文本
                for span in intro_el.select('span.short, span.all'):
                    span.decompose()
                description = intro_el.get_text('\n', strip=True)

            # info 区块
            info_text = ''
            info_el = soup.select_one('#info')
            if info_el:
                info_text = info_el.get_text('\n', strip=True)

            def extract(pattern):
                m = re.search(pattern, info_text)
                return m.group(1).strip() if m else ''

            author = extract(r'作者[:：]\s*([^\n]+)')
            pub_year_str = extract(r'出版年[:：]\s*([^\n]+)')
            isbn = extract(r'ISBN[:：]\s*([^\n]+)')
            
            # 解析年份为整数
            pub_year = None
            if pub_year_str:
                year_match = re.search(r'\d{4}', pub_year_str)
                if year_match:
                    try:
                        pub_year = int(year_match.group())
                    except:
                        pass

            return {
                'author': author,
                'publication_year': pub_year,
                'isbn': isbn,
                'cover_url': cover_url,
                'description': description,
            }

        except Exception as e:
            self.safe_write(f'  解析详情页失败: {str(e)}', self.style.WARNING)
            return None
