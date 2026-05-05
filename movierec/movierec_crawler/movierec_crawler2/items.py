import scrapy


class DoubanMovieItem(scrapy.Item):
    """豆瓣电影基础信息"""

    source = scrapy.Field()
    movie_url = scrapy.Field()
    title = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
    cover_url = scrapy.Field()
    description = scrapy.Field()
    release_date = scrapy.Field()
    genres = scrapy.Field()
    duration = scrapy.Field()
    rating_avg = scrapy.Field()
    rating_people = scrapy.Field()
    crawled_at = scrapy.Field()
    # 可选：从 movies.txt 继承的顺序编号
    seq = scrapy.Field()


class DoubanMovieCommentItem(scrapy.Item):
    """豆瓣电影短评（可选）"""

    movie_url = scrapy.Field()
    user = scrapy.Field()
    content = scrapy.Field()
    created_at = scrapy.Field()
    source = scrapy.Field()
