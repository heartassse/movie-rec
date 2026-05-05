"""
Scrapy settings for movierec_crawler2 project.

这是一个偏“保守、稳一点”的默认配置，你可以根据自己的代理、Cookie、
封禁情况再调整并发、延迟等参数。
"""

BOT_NAME = "movierec_crawler2"

SPIDER_MODULES = ["movierec_crawler2.spiders"]
NEWSPIDER_MODULE = "movierec_crawler2.spiders"

# 供中间件定位相对路径使用
PROJECT_ROOT = "."
# 避免明显表明是 Scrapy
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

ROBOTSTXT_OBEY = False

# 并发与延迟：先非常保守，后面可以慢慢调
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 3.0  # 单域名 3 秒一请求左右

CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS_PER_IP = 0

COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
    # 动态代理 & Cookie
    "movierec_crawler2.middlewares.RotatingProxyMiddleware": 610,
    "movierec_crawler2.middlewares.RotatingCookieMiddleware": 620,
}

RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [403, 418, 429, 500, 502, 503, 504]

ITEM_PIPELINES = {
    "movierec_crawler2.pipelines.JsonLinesPipeline": 300,
}

LOG_LEVEL = "INFO"

# ===== 动态代理 & 动态 Cookie 默认配置（可在命令行或 settings 覆盖） =====

# 代理列表文件：每行一个代理，例如：
#   http://ip:port
#   http://user:pass@ip:port
# 建议放在项目根目录，例如 proxies.txt
ROTATING_PROXY_FILE = "proxies.txt"

# Cookie 列表文件：每行一整条 Cookie 头的值（浏览器 F12 复制的那一长串）
ROTATING_COOKIE_FILE = "cookies_pool.txt"

# 每多少个请求轮换一次 Cookie
ROTATING_COOKIE_EVERY = 20

