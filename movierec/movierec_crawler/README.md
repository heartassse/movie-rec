# 豆瓣电影爬虫项目

基于 Scrapy 框架的豆瓣电影数据爬虫，可自动获取电影信息、评分、评论等数据。

## 快速开始

### 安装依赖

```bash
pip install scrapy beautifulsoup4 lxml
```

### 执行爬虫

#### 1. 爬取电影列表（最简单）

```bash
# 爬取"科幻"标签下的电影（前 3 页）
scrapy crawl douban_movies -a tags=科幻 -a max_pages=3 -a out_dir=data_raw_scrapy
```

#### 2. 爬取多个标签

```bash
# 同时爬取多个标签下的电影
scrapy crawl douban_movies -a tags=科幻,剧情,喜剧,爱情,动作 -a max_pages=5 -a out_dir=data_raw_scrapy
```

#### 3. 爬取电影和短评

```bash
# 爬取电影并获取每部电影的前 20 条短评
scrapy crawl douban_movies \
  -a tags=科幻,剧情 \
  -a max_pages=5 \
  -a comment_pages=1 \
  -a comments_per_movie=20 \
  -a out_dir=data_raw_scrapy
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `tags` | 科幻,剧情,喜剧,爱情,动作 | 要爬取的标签，多个用逗号分隔 |
| `max_pages` | 3 | 每个标签爬取的页数（每页 20 部电影） |
| `comment_pages` | 0 | 是否爬取短评（0=不爬，1=爬一页） |
| `comments_per_movie` | 20 | 每部电影爬取多少条短评 |
| `out_dir` | data_raw_scrapy | 输出数据的目录 |
| `target_total` | 30000 | 目标数据总量（电影数 + 短评数） |

### 输出格式

爬虫会生成两个 JSONL 文件：

#### movies.jsonl - 电影数据

```json
{
  "source": "douban",
  "movie_url": "https://movie.douban.com/subject/1292052/",
  "title": "肖申克的救赎",
  "directors": "弗兰克·德拉邦特",
  "actors": "蒂姆·罗宾斯 / 摩根·弗里曼",
  "cover_url": "https://img9.doubanio.com/view/photo/...",
  "description": "20世纪40年代末...",
  "release_date": "1994-09-10",
  "genres": "剧情 / 犯罪",
  "duration": "142分钟",
  "rating_avg": "9.7",
  "rating_people": "300万人评价",
  "crawled_at": "2026-03-01T15:30:45.123456"
}
```

#### comments.jsonl - 短评数据

```json
{
  "movie_url": "https://movie.douban.com/subject/1292052/",
  "user": "用户昵称",
  "content": "希望是美好的，也许是人间至善...",
  "created_at": "2024-02-28",
  "source": "douban"
}
```

## 进阶使用

### 使用代理池

如果被豆瓣限流，可以使用代理池：

```bash
# 1. 编辑 proxies.txt 添加代理列表
# 2. 运行爬虫时指定代理文件
scrapy crawl douban_movies -a proxy_file=proxies.txt -a tags=科幻 -a max_pages=10
```

### 使用 Cookie 池

```bash
# 1. 编辑 cookies_pool.txt 添加多个账号的 Cookie
# 2. 运行爬虫时指定 Cookie 文件
scrapy crawl douban_movies -a cookie_file=cookies_pool.txt -a tags=科幻 -a max_pages=10
```

## 导入到数据库

爬取完成后，可以将数据导入到系统数据库：

```bash
# 在后端目录运行
cd ../movierec_backend

# 爬取的数据需自行转换为 SQL 或通过其他方式导入
# 本系统数据主要通过 SQL 文件导入：mysql -u root -p movierec_dev < 备份.sql
```

## 遵守爬虫礼仪

- ✅ 遵守豆瓣 robots.txt 规则
- ✅ 设置合理的延迟（默认 3 秒/请求）
- ✅ 使用正确的 User-Agent
- ✅ 不要频繁请求同一资源
- ✅ 尊重网站 ToS

## 常见问题

### Q: 爬虫被限流了怎么办？
A: 
1. 增加请求延迟：修改 `settings.py` 中的 `DOWNLOAD_DELAY`
2. 使用代理池：编辑 `proxies.txt` 并指定 `-a proxy_file=proxies.txt` 参数
3. 使用 Cookie 池：编辑 `cookies_pool.txt` 并指定 `-a cookie_file=cookies_pool.txt` 参数

### Q: 数据不完整怎么办？
A: 尝试再次运行爬虫，已成功的数据会追加到输出文件

### Q: 如何只爬取特定信息？
A: 编辑 `bookrec_crawler2/spiders/douban_movies.py`，修改 `parse_movie_detail` 方法
