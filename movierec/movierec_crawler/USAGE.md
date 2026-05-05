# 豆瓣电影爬虫配置说明

## 项目结构

```
movierec_crawler/
├── bookrec_crawler2/          # 项目核心代码（Scrapy 包名）
│   ├── spiders/
│   │   ├── douban_movies.py           # 豆瓣电影爬虫
│   │   └── douban_movies_from_list.py # 根据片单爬取（备用）
│   ├── items.py                # 数据模型定义
│   ├── pipelines.py            # 数据处理管道
│   ├── middlewares.py          # 中间件（代理、Cookie 等）
│   └── settings.py             # Scrapy 配置
├── data_raw_scrapy/            # 爬虫输出数据
│   ├── movies.jsonl            # 电影数据（JSONL 格式）
│   └── comments.jsonl         # 短评数据（JSONL 格式）
├── proxies.txt.example         # 代理列表示例
├── cookies_pool.txt.example    # Cookie 池示例
├── scrapy.cfg                  # Scrapy 项目配置
└── README.md                   # 项目说明
```

## 配置文件

### proxies.txt - 代理列表

格式：每行一个代理（IP:PORT）

```
10.10.0.1:8080
10.10.0.2:8080
10.10.0.3:8080
```

### cookies_pool.txt - Cookie 池

格式：每行一个 Cookie 字符串

```
cookie1=value1; cookie2=value2; ...
cookie1=value1_alt; cookie2=value2_alt; ...
```

## 数据格式

### movies.jsonl

```json
{
  "source": "douban",                           // 数据来源
  "movie_url": "https://movie.douban.com/subject/1292052/",
  "title": "肖申克的救赎",                        // 片名
  "directors": "弗兰克·德拉邦特",                 // 导演
  "actors": "蒂姆·罗宾斯 / 摩根·弗里曼",          // 主演
  "cover_url": "https://img9.doubanio.com/...", // 封面 URL
  "description": "20世纪40年代末...",            // 电影简介
  "release_date": "1994-09-10",                 // 上映日期
  "genres": "剧情 / 犯罪",                       // 类型
  "duration": "142分钟",                        // 片长
  "rating_avg": "9.7",                          // 平均评分
  "rating_people": "300万人评价",                // 评价人数
  "crawled_at": "2026-03-01T15:30:45.123456"   // 爬取时间
}
```

### comments.jsonl

```json
{
  "movie_url": "https://movie.douban.com/subject/1292052/",
  "user": "用户昵称",                             // 评论者
  "content": "希望是美好的，也许是人间至善...",     // 评论内容
  "created_at": "2024-02-28",                    // 创建时间
  "source": "douban"                             // 数据来源
}
```

## 高级设置

### settings.py 主要配置项

```python
# 下载延迟（秒）
DOWNLOAD_DELAY = 3

# 并发请求数
CONCURRENT_REQUESTS = 4

# 重试次数
RETRY_TIMES = 3

# 使用代理
ROTATING_PROXY_FILE = 'proxies.txt'

# 使用 Cookie 池
ROTATING_COOKIE_FILE = 'cookies_pool.txt'
```

## 常见错误排查

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 403 Forbidden | IP 被豆瓣屏蔽 | 使用代理池或增加延迟 |
| 429 Too Many Requests | 请求过于频繁 | 增加 DOWNLOAD_DELAY |
| 爬虫不启动 | 依赖未安装 | 运行 `pip install scrapy beautifulsoup4 lxml` |

## 性能优化

1. **调整并发数**：如果服务器有多核，可增加 `CONCURRENT_REQUESTS`
2. **使用代理**：分散请求来源，避免被限制
3. **合理设置延迟**：平衡速度和被屏蔽的风险
4. **使用管道优化**：在 `pipelines.py` 中进行数据验证和去重

## 合规性说明

- 本爬虫仅用于学习和研究目的
- 遵守豆瓣网站的 robots.txt 和 ToS
- 爬取的数据仅供学术研究使用
- 不得用于商业用途
