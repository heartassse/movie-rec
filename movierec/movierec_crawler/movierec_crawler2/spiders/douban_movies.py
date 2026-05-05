import re
from datetime import datetime
from urllib.parse import quote

import scrapy
from bs4 import BeautifulSoup
from scrapy.exceptions import CloseSpider

from movierec_crawler2.items import DoubanMovieItem, DoubanMovieCommentItem


class DoubanMoviesSpider(scrapy.Spider):
    """
    豆瓣电影 Scrapy 爬虫：
    - 按 tag 抓取电影列表页
    - 进入电影详情页抓取电影信息
    - （可选）抓取短评

    使用方式（在 movierec_crawler 目录下终端执行）：
        scrapy crawl douban_movies -a tags=科幻,剧情,喜剧 -a max_pages=3 -a out_dir=data_raw_scrapy
    """

    name = "douban_movies"
    allowed_domains = ["movie.douban.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 3.0,
        "CONCURRENT_REQUESTS": 4,
    }

    def __init__(
        self,
        tags: str = "科幻,剧情,喜剧,爱情,动作",
        max_pages: int = 3,
        comment_pages: int = 0,
        out_dir: str = "data_raw_scrapy",
        proxy_file: str = "",
        cookie_file: str = "",
        target_total: int = 30000,
        comments_per_movie: int = 20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tags = [t.strip() for t in tags.split(",") if t.strip()]
        self.max_pages = int(max_pages)
        self.comment_pages = max(0, int(comment_pages))
        self.out_dir = out_dir
        self.target_total = int(target_total)
        self.comments_per_movie = int(comments_per_movie)
        self.movie_count = 0
        self.comment_count = 0

        if proxy_file:
            self.custom_settings = {**self.custom_settings, "ROTATING_PROXY_FILE": proxy_file}
        if cookie_file:
            self.custom_settings = {**self.custom_settings, "ROTATING_COOKIE_FILE": cookie_file}

    def _should_stop(self) -> bool:
        return (self.movie_count + self.comment_count) >= self.target_total

    def start_requests(self):
        for tag in self.tags:
            encoded_tag = quote(tag, safe="")
            for page in range(self.max_pages):
                start = page * 20
                url = f"https://movie.douban.com/tag/{encoded_tag}?start={start}&type=T"
                yield scrapy.Request(
                    url,
                    headers={"Referer": f"https://movie.douban.com/tag/{encoded_tag}"},
                    callback=self.parse_tag_list,
                    cb_kwargs={"tag": tag, "page": page},
                )

    def parse_tag_list(self, response, tag: str, page: int):
        if self._should_stop():
            raise CloseSpider(reason="target_total_reached")

        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.select("a.nbg"):
            href = a.get("href")
            if href and "movie.douban.com/subject/" in href:
                links.append(href.split("?")[0].rstrip("/"))
        if not links:
            for a in soup.select("a[href*='movie.douban.com/subject/']"):
                href = a.get("href")
                if href:
                    links.append(href.split("?")[0].rstrip("/"))

        seen = set()
        for link in links:
            if link not in seen:
                seen.add(link)
                if self._should_stop():
                    raise CloseSpider(reason="target_total_reached")
                yield scrapy.Request(link, callback=self.parse_movie_detail, cb_kwargs={"movie_url": link})

    def parse_movie_detail(self, response, movie_url: str):
        soup = BeautifulSoup(response.text, "html.parser")

        def _safe(sel):
            return sel.get_text(strip=True) if sel else ""

        title = _safe(soup.select_one("h1 span"))
        cover = soup.select_one("#mainpic img")
        cover_url = cover.get("src", "") if cover else ""
        rating_avg = _safe(soup.select_one("strong.ll.rating_num"))
        rating_people = _safe(soup.select_one("a.rating_people span"))
        intro_el = soup.select_one("#link-report .intro")
        intro = intro_el.get_text("\n", strip=True) if intro_el else ""
        info_text = _safe(soup.select_one("#info"))

        def _extract(pattern: str) -> str:
            m = re.search(pattern, info_text)
            return m.group(1).strip() if m else ""

        item = DoubanMovieItem(
            source="douban",
            movie_url=movie_url,
            title=title,
            directors=_extract(r"导演[:：]\s*([^\n]+)"),
            actors=_extract(r"主演[:：]\s*([^\n]+)"),
            cover_url=cover_url,
            description=intro,
            release_date=_extract(r"上映日期[:：]\s*([^\n]+)"),
            genres=_extract(r"类型[:：]\s*([^\n]+)"),
            duration=_extract(r"片长[:：]\s*([^\n]+)"),
            rating_avg=rating_avg,
            rating_people=rating_people,
            crawled_at=datetime.utcnow().isoformat(),
        )
        self.movie_count += 1
        yield item

        if self.comment_pages > 0 and not self._should_stop():
            subject_id = movie_url.rstrip("/").split("/")[-1]
            url = f"https://movie.douban.com/subject/{subject_id}/comments/?start=0&limit={self.comments_per_movie}&status=P&sort=new_score"
            yield scrapy.Request(url, callback=self.parse_short_comments, cb_kwargs={"movie_url": movie_url})

    def parse_short_comments(self, response, movie_url: str):
        soup = BeautifulSoup(response.text, "html.parser")

        def _safe(sel):
            return sel.get_text(strip=True) if sel else ""

        for item_el in soup.select("div.comment-item"):
            if self._should_stop():
                raise CloseSpider(reason="target_total_reached")
            self.comment_count += 1
            yield DoubanMovieCommentItem(
                movie_url=movie_url,
                user=_safe(item_el.select_one("span.comment-info a")),
                content=_safe(item_el.select_one("span.short")),
                created_at=_safe(item_el.select_one("span.comment-time")),
                source="douban",
            )
