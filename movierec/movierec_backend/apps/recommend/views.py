from django.db.models import Avg, Count, Case, When, IntegerField, Value
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import jieba
import re
from collections import Counter

from apps.books.models import Book
from apps.books.serializers import BookSerializer, BookWithStatsSerializer
from apps.ratings.models import Rating, Comment
from .algorithms import UserCF, ItemCF, HybridRecommender

User = get_user_model()


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def hot_books(request):
    """占位推荐：返回热门电影。

    热门定义：按评分次数、平均分排序。
    - 评分次数多优先
    - 平均分高优先
    """

    try:
        limit = int(request.query_params.get("limit", "10"))
    except ValueError:
        limit = 10

    if limit < 1:
        limit = 10
    if limit > 50:
        limit = 50

    # 使用缓存，5分钟过期
    cache_key = f'hot_books:{limit}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)

    qs = (
        Book.objects.annotate(
            rating_count=Count("ratings"),
            rating_avg=Avg("ratings__score"),
            comment_count=Count("comments", distinct=True),
        )
        .order_by("-rating_count", "-rating_avg", "-created_at")
    )

    items = list(qs[:limit])
    
    result = {
        "limit": limit,
        "results": BookWithStatsSerializer(items, many=True).data,
    }
    
    # 缓存结果
    cache.set(cache_key, result, 300)  # 5分钟

    return Response(result)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_recommendations(request):
    """
    基于 UserCF 的个性化推荐
    
    支持参数：
    - limit: 推荐数量，默认10
    - method: 相似度计算方法 ('cosine' 或 'pearson')，默认 'cosine'
    - normalize: 是否归一化评分，默认 true
    - k: 选取的相似用户数量，默认30
    """
    
    limit = min(max(int(request.query_params.get("limit", 10)), 1), 50)
    method = request.query_params.get("method", "cosine")
    normalize = request.query_params.get("normalize", "true").lower() == "true"
    k_neighbors = min(max(int(request.query_params.get("k", 30)), 5), 100)
    
    user_id = request.user.id
    
    # 检查缓存
    cache_key = f'user_rec:{user_id}:{method}:{normalize}:{k_neighbors}:{limit}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)
    
    # 获取所有评分数据
    ratings = list(Rating.objects.values("user_id", "book_id", "score"))
    if not ratings:
        return hot_books(request)
    
    # 检查用户是否有评分
    user_has_ratings = any(r['user_id'] == user_id for r in ratings)
    if not user_has_ratings:
        return hot_books(request)
    
    # 使用UserCF算法
    user_cf = UserCF(
        similarity_method=method,
        normalize=normalize,
        k_neighbors=k_neighbors,
        min_common_items=3
    )
    
    # 训练模型
    user_cf.fit([
        {'user_id': r['user_id'], 'item_id': r['book_id'], 'score': r['score']}
        for r in ratings
    ])
    
    # 生成推荐
    recommendations = user_cf.recommend(user_id, top_n=limit * 2)
    
    if not recommendations:
        return hot_books(request)
    
    # 获取推荐电影
    rec_ids = [item_id for item_id, _ in recommendations]
    books = Book.objects.filter(id__in=rec_ids)
    books = sorted(books, key=lambda x: rec_ids.index(x.id))
    
    result = {
        "limit": limit,
        "method": method,
        "normalize": normalize,
        "k_neighbors": k_neighbors,
        "results": BookSerializer(books[:limit], many=True).data
    }
    
    # 缓存结果（2分钟）
    cache.set(cache_key, result, 120)
    
    return Response(result)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def similar_books(request):
    """
    基于 ItemCF 的相似电影推荐
    
    支持参数：
    - book_id: 目标电影ID（必需）
    - limit: 推荐数量，默认10
    - method: 相似度计算方法 ('cosine' 或 'pearson')，默认 'cosine'
    - adjusted: 是否使用调整余弦相似度，默认 true
    - k: 选取的相似物品数量，默认20
    """
    
    try:
        book_id = int(request.query_params.get("book_id", ""))
    except ValueError:
        return Response({"detail": "book_id is required"}, status=400)
    
    limit = min(max(int(request.query_params.get("limit", 10)), 1), 30)
    method = request.query_params.get("method", "cosine")
    use_adjusted = request.query_params.get("adjusted", "true").lower() == "true"
    k_neighbors = min(max(int(request.query_params.get("k", 20)), 5), 50)
    
    # 检查缓存
    cache_key = f'similar_books:{book_id}:{method}:{use_adjusted}:{k_neighbors}:{limit}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)
    
    # 优化：只获取与目标电影相关的用户的评分
    target_users = Rating.objects.filter(book_id=book_id).values_list("user_id", flat=True)
    if not target_users:
        return hot_books(request)
    
    # 只查询这些用户的评分，大幅减少数据量
    ratings = list(Rating.objects.filter(user_id__in=list(target_users)).values("user_id", "book_id", "score"))
    if not ratings:
        return hot_books(request)
    
    # 使用ItemCF算法
    item_cf = ItemCF(
        similarity_method=method,
        use_adjusted=use_adjusted,
        k_neighbors=k_neighbors,
        min_common_users=3
    )
    
    # 训练模型
    item_cf.fit([
        {'user_id': r['user_id'], 'item_id': r['book_id'], 'score': r['score']}
        for r in ratings
    ])
    
    # 获取相似电影
    similar_items = item_cf.get_similar_items(book_id, top_n=limit * 2)
    
    if not similar_items:
        return hot_books(request)
    
    # 获取推荐电影（含评分统计）
    rec_ids = [item_id for item_id, _ in similar_items]
    books = (
        Book.objects.filter(id__in=rec_ids)
        .annotate(
            rating_count=Count("ratings"),
            rating_avg=Avg("ratings__score"),
            comment_count=Count("comments", distinct=True),
        )
    )
    books = sorted(books, key=lambda x: rec_ids.index(x.id))
    
    result = {
        "limit": limit,
        "method": method,
        "use_adjusted": use_adjusted,
        "k_neighbors": k_neighbors,
        "results": BookWithStatsSerializer(books[:limit], many=True).data
    }
    
    # 缓存结果（5分钟）
    cache.set(cache_key, result, 300)
    
    return Response(result)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def hybrid_recommendations(request):
    """
    混合推荐：结合 UserCF 和 ItemCF
    
    支持参数：
    - limit: 推荐数量，默认10
    - user_weight: UserCF权重，默认0.5
    - item_weight: ItemCF权重，默认0.5
    - method: 相似度计算方法 ('cosine' 或 'pearson')，默认 'cosine'
    """
    
    limit = min(max(int(request.query_params.get("limit", 10)), 1), 50)
    user_weight = float(request.query_params.get("user_weight", 0.5))
    item_weight = float(request.query_params.get("item_weight", 0.5))
    method = request.query_params.get("method", "cosine")
    
    user_id = request.user.id
    
    # 检查缓存
    cache_key = f'hybrid_rec:{user_id}:{method}:{user_weight}:{item_weight}:{limit}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)
    
    # 获取所有评分数据
    ratings = list(Rating.objects.values("user_id", "book_id", "score"))
    if not ratings:
        return hot_books(request)
    
    # 检查用户是否有评分
    user_rated_items = {}
    for r in ratings:
        if r['user_id'] == user_id:
            user_rated_items[r['book_id']] = float(r['score'])
    
    if not user_rated_items:
        return hot_books(request)
    
    # 初始化UserCF
    user_cf = UserCF(
        similarity_method=method,
        normalize=True,
        k_neighbors=30,
        min_common_items=3
    )
    
    # 初始化ItemCF
    item_cf = ItemCF(
        similarity_method=method,
        use_adjusted=True,
        k_neighbors=20,
        min_common_users=3
    )
    
    # 训练模型
    rating_data = [
        {'user_id': r['user_id'], 'item_id': r['book_id'], 'score': r['score']}
        for r in ratings
    ]
    user_cf.fit(rating_data)
    item_cf.fit(rating_data)
    
    # 创建混合推荐器
    hybrid = HybridRecommender(user_cf, item_cf, user_weight, item_weight)
    
    # 生成推荐
    recommendations = hybrid.recommend(user_id, user_rated_items, top_n=limit * 2)
    
    if not recommendations:
        return hot_books(request)
    
    # 获取推荐电影
    rec_ids = [item_id for item_id, _ in recommendations]
    books = Book.objects.filter(id__in=rec_ids)
    books = sorted(books, key=lambda x: rec_ids.index(x.id))
    
    result = {
        "limit": limit,
        "method": method,
        "user_weight": user_weight,
        "item_weight": item_weight,
        "results": BookSerializer(books[:limit], many=True).data
    }
    
    # 缓存结果（2分钟）
    cache.set(cache_key, result, 120)
    
    return Response(result)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def stats_overview(request):
    """可视化概览统计：评分分布、热门Top10、（近似）分类占比。

    注：当前 Book 模型未定义 category 字段，因此分类占比使用“出版年代”做近似分组。
    """

    # 总数统计
    total_users = User.objects.count()
    total_books = Book.objects.count()
    total_ratings = Rating.objects.count()
    total_comments = Comment.objects.count()

    # 评分分布（1~5）
    dist = (
        Book.objects.values("ratings__score")
        .exclude(ratings__score__isnull=True)
        .annotate(count=Count("ratings__score"))
        .order_by("ratings__score")
    )
    rating_distribution = [
        {"score": int(x["ratings__score"]), "count": int(x["count"])} for x in dist if x["ratings__score"] is not None
    ]

    # 热门Top10：按评分次数
    hot_qs = (
        Book.objects.annotate(rating_count=Count("ratings"))
        .order_by("-rating_count", "-created_at")
        .values("id", "title", "rating_count")[:10]
    )
    hot_top10 = [{"id": x["id"], "title": x["title"], "count": int(x["rating_count"])} for x in hot_qs]

    # “分类占比”近似：出版年代（1900s/2000s/未知）
    years = Book.objects.values_list("publication_year", flat=True)
    buckets = {}
    for y in years:
        if not y:
            k = "未知"
        else:
            decade = int(y) // 10 * 10
            k = f"{decade}s"
        buckets[k] = buckets.get(k, 0) + 1
    category_share = [{"name": k, "value": v} for k, v in sorted(buckets.items(), key=lambda x: (-x[1], x[0]))]

    # 2. 好评最多的电影 Top10（平均评分 >= 4.0，且评分人数 >= 5）
    high_rated_books = (
        Book.objects.annotate(
            avg_score=Avg("ratings__score"),
            rating_count=Count("ratings")
        )
        .filter(avg_score__gte=4.0, rating_count__gte=5)
        .order_by("-avg_score", "-rating_count")
        .values("id", "title", "avg_score", "rating_count")[:10]
    )
    top_rated = [
        {
            "id": x["id"],
            "title": x["title"],
            "avg_score": round(float(x["avg_score"]), 2),
            "rating_count": int(x["rating_count"])
        }
        for x in high_rated_books
    ]

    # 3. 最受欢迎的电影 Top10（评分次数最多）
    most_popular = [{"id": x["id"], "title": x["title"], "count": int(x["rating_count"])} for x in hot_qs]

    # 4. 评论最多的电影 Top10
    most_commented = (
        Book.objects.annotate(comment_count=Count("comments"))
        .filter(comment_count__gt=0)
        .order_by("-comment_count")
        .values("id", "title", "comment_count")[:10]
    )
    top_commented = [{"id": x["id"], "title": x["title"], "count": int(x["comment_count"])} for x in most_commented]

    # 5. 电影平均评分分布（分段统计）
    books_with_ratings = Book.objects.annotate(avg_score=Avg("ratings__score")).filter(avg_score__isnull=False)
    
    # 使用数据库聚合而不是Python循环
    score_distribution_query = books_with_ratings.aggregate(
        star_5_0=Count(Case(When(avg_score__gte=5.0, then=1), output_field=IntegerField())),
        star_4_5_4_9=Count(Case(When(avg_score__gte=4.5, avg_score__lt=5.0, then=1), output_field=IntegerField())),
        star_4_0_4_4=Count(Case(When(avg_score__gte=4.0, avg_score__lt=4.5, then=1), output_field=IntegerField())),
        star_3_5_3_9=Count(Case(When(avg_score__gte=3.5, avg_score__lt=4.0, then=1), output_field=IntegerField())),
        star_3_0_3_4=Count(Case(When(avg_score__gte=3.0, avg_score__lt=3.5, then=1), output_field=IntegerField())),
        star_below_3_0=Count(Case(When(avg_score__lt=3.0, then=1), output_field=IntegerField())),
    )
    
    book_score_distribution = [
        {"range": "5.0星", "count": score_distribution_query['star_5_0']},
        {"range": "4.5-4.9星", "count": score_distribution_query['star_4_5_4_9']},
        {"range": "4.0-4.4星", "count": score_distribution_query['star_4_0_4_4']},
        {"range": "3.5-3.9星", "count": score_distribution_query['star_3_5_3_9']},
        {"range": "3.0-3.4星", "count": score_distribution_query['star_3_0_3_4']},
        {"range": "3.0星以下", "count": score_distribution_query['star_below_3_0']},
    ]

    # 6. 上映年代分布
    year_distribution = category_share

    return Response(
        {
            "total_users": total_users,
            "total_books": total_books,
            "total_ratings": total_ratings,
            "total_comments": total_comments,
            "ratingDistribution": rating_distribution,
            "topRated": top_rated,
            "mostPopular": most_popular,
            "topCommented": top_commented,
            "movieScoreDistribution": book_score_distribution,
            "bookScoreDistribution": book_score_distribution,
            "yearDistribution": year_distribution,
            "hotTop10": hot_top10,
            "categoryShare": category_share,
        }
    )


# 停用词列表（可根据需要扩展）
STOP_WORDS = {
    '的', '了', '和', '是', '在', '有', '我', '你', '他', '她', '它', '们',
    '这', '那', '之', '与', '及', '等', '中', '为', '以', '上', '下', '到',
    '对', '把', '被', '从', '向', '由', '于', '给', '让', '使', '将', '而',
    '或', '但', '也', '都', '很', '就', '还', '要', '会', '能', '可', '不',
    '没', '吗', '呢', '吧', '啊', '哦', '嗯', '哈', '呀', '啦', '嘛', '呐',
}


def _tokenize_and_count(text, min_word_len=2):
    """分词并统计词频，过滤停用词和短词。"""
    if not text:
        return Counter()
    
    words = jieba.cut(text)
    filtered = [
        w.strip() for w in words 
        if len(w.strip()) >= min_word_len and w.strip() not in STOP_WORDS
    ]
    return Counter(filtered)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def wordcloud_data(request):
    """词云数据接口：支持多数据源切换。
    
    参数：
    - source: 数据源类型，可选值：titles（电影名）、descriptions（简介）、comments（评论）、authors（作者）
    - limit: 返回词频Top N，默认100
    """
    
    source = request.query_params.get("source", "titles")
    try:
        limit = int(request.query_params.get("limit", "100"))
    except ValueError:
        limit = 100
    
    limit = min(max(limit, 10), 500)
    
    counter = Counter()
    
    if source == "titles":
        titles = Book.objects.values_list("title", flat=True)
        for title in titles:
            if title:
                counter.update(_tokenize_and_count(title))
    
    elif source == "descriptions":
        descriptions = Book.objects.exclude(description__isnull=True).exclude(description="").values_list("description", flat=True)
        for desc in descriptions:
            if desc:
                counter.update(_tokenize_and_count(desc))
    
    elif source == "comments":
        comments = Comment.objects.values_list("content", flat=True)
        for content in comments:
            if content:
                counter.update(_tokenize_and_count(content))
    
    elif source == "authors":
        authors = Book.objects.values_list("author", flat=True)
        for author in authors:
            if author:
                counter.update(_tokenize_and_count(author, min_word_len=1))
    
    else:
        return Response({"detail": "Invalid source parameter"}, status=400)
    
    top_words = counter.most_common(limit)
    word_data = [{"name": word, "value": count} for word, count in top_words]
    
    return Response({
        "source": source,
        "limit": limit,
        "total_words": len(counter),
        "data": word_data
    })