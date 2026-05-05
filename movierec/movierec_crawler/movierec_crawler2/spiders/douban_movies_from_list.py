import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import scrapy
from bs4 import BeautifulSoup

from movierec_crawler2.items import DoubanMovieItem


class DoubanMoviesFromListSpider(scrapy.Spider):
    """
    根据现有 movies.txt 的电影名顺序，在豆瓣搜索并抓取电影封面 URL 和简介等信息。

    使用方式（在 movierec_crawler 目录下）：
        scrapy crawl douban_movies_from_list \
          -a movies_file=../movierec_backend/movies.txt \
          -a out_dir=data_raw_scrapy_from_list

    只依赖电影名，不使用 tag 列表；会尽量保持与 movies.txt 中的顺序一致。
    """

    name = "douban_movies_from_list"
    allowed_domains = ["movie.douban.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 3.0,
        "CONCURRENT_REQUESTS": 4,
    }

    def __init__(
        self,
        movies_file: str = "../movierec_backend/movies.txt",
        out_dir: str = "data_raw_scrapy_from_list",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.movies_file = movies_file
        self.out_dir = out_dir
        self.movie_list = []

    def start_requests(self):
        path = Path(self.movies_file)
        if not path.is_absolute():
            path = Path(".") / path

        if not path.exists():
            self.logger.error("movies_file 不存在: %s", path)
            return

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r"^(\d+)\.\s*(.+?)(?:\s*\[.*\])?$", line)
                if not m:
                    continue
                idx = int(m.group(1))
                title = m.group(2).strip("《》\"\"")
                self.movie_list.append((idx, title))

        self.logger.info("从 %s 读取到 %s 部电影名", path, len(self.movie_list))

        for idx, title in self.movie_list:
            query = quote(title)
            url = f"https://movie.douban.com/j/subject_search?search_text={query}&cat=1002"
            yield scrapy.Request(
                url,
                callback=self.parse_search,
                cb_kwargs={"seq": idx, "title": title},
            )

    def parse_search(self, response, seq: int, title: str):
        """解析豆瓣电影搜索结果，找到第一个电影 subject 链接。"""
        import json
        try:
            data = json.loads(response.text)
            subjects = data.get("subjects", [])
        except Exception:
            self.logger.warning("搜索 JSON 解析失败: seq=%s title=%s", seq, title)
            return

        if not subjects:
            self.logger.warning("搜索不到结果: seq=%s title=%s", seq, title)
            return

        movie_url = subjects[0].get("url", "").split("?")[0].rstrip("/")
        if not movie_url:
            return
        yield scrapy.Request(
            movie_url,
            callback=self.parse_movie_detail,
            cb_kwargs={"seq": seq, "orig_title": title, "movie_url": movie_url},
        )

    def parse_movie_detail(self, response, seq: int, orig_title: str, movie_url: str):
        soup = BeautifulSoup(response.text, "html.parser")

        def _safe(sel):
            return sel.get_text(strip=True) if sel else ""

        title = _safe(soup.select_one("h1 span")) or orig_title
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
        item["seq"] = seq
        yield item
