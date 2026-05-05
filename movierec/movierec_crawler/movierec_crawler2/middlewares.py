import logging
import random
from pathlib import Path
from typing import List, Optional

from scrapy import Request

logger = logging.getLogger(__name__)


class RotatingProxyMiddleware:
    """
    简单版代理轮换中间件：
    - 从文件读取代理列表（每行一个，如 http://user:pass@ip:port 或 http://ip:port）
    - 每个请求随机挑选一个代理
    - 若响应状态码在 ban 列表中，可在 settings 里再叠加 BanDetectionMiddleware 之类做更复杂策略
    """

    def __init__(self, proxies: List[str]):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler):
        proxy_file = crawler.settings.get("ROTATING_PROXY_FILE")
        proxies: List[str] = []

        if proxy_file:
            path = Path(proxy_file)
            if not path.is_absolute():
                # 相对路径相对于项目根目录
                path = Path(crawler.settings.get("PROJECT_ROOT", ".")) / path
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            proxies.append(line)

        if not proxies:
            logger.info("[RotatingProxy] 未加载到代理列表，将使用直连")

        return cls(proxies)

    def process_request(self, request: Request, spider):
        if not self.proxies:
            return
        proxy = random.choice(self.proxies)
        request.meta["proxy"] = proxy


class RotatingCookieMiddleware:
    """
    简单版 Cookie 轮换中间件：
    - 从文件读取多个 Cookie（每行一条完整的 Cookie 头内容）
    - 每 N 个请求轮换一次，或每次随机选择
    """

    def __init__(self, cookies: List[str], rotate_every: int = 20):
        self.cookies = cookies
        self.rotate_every = max(1, rotate_every)
        self.request_count = 0
        self._current_cookie: Optional[str] = None

    @classmethod
    def from_crawler(cls, crawler):
        cookie_file = crawler.settings.get("ROTATING_COOKIE_FILE")
        rotate_every = crawler.settings.getint("ROTATING_COOKIE_EVERY", 20)
        cookies: List[str] = []

        if cookie_file:
            path = Path(cookie_file)
            if not path.is_absolute():
                path = Path(crawler.settings.get("PROJECT_ROOT", ".")) / path
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            cookies.append(line)

        if not cookies:
            logger.info("[RotatingCookie] 未加载到 Cookie 列表，将不主动设置 Cookie")

        return cls(cookies, rotate_every=rotate_every)

    def _choose_cookie(self) -> Optional[str]:
        if not self.cookies:
            return None
        # 简单策略：每 rotate_every 次请求随机换一个
        if self._current_cookie is None or self.request_count % self.rotate_every == 0:
            self._current_cookie = random.choice(self.cookies)
        return self._current_cookie

    def process_request(self, request: Request, spider):
        self.request_count += 1
        cookie = self._choose_cookie()
        if not cookie:
            return

        # 如果 request 自己已经设置了 Cookie，以 request 为准，不覆盖
        if "Cookie" in request.headers:
            return

        request.headers["Cookie"] = cookie

