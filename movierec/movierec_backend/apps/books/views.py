from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Book
from .serializers import BookSerializer, BookListSerializer
from apps.ratings.models import Rating


class StandardPageNumberPagination(PageNumberPagination):
    """标准分页器（优化性能）"""
    page_size = 20  # 默认每页20条，减少单次请求数据量
    page_size_query_param = 'page_size'  # 允许客户端指定页面大小
    max_page_size = 50000  # 最大页面大小限制（搜索页可加载全部电影）


class LargePageNumberPagination(PageNumberPagination):
    """大页面分页器（用于管理后台）"""
    page_size = 50  # 默认每页50条
    page_size_query_param = 'page_size'
    max_page_size = 200  # 最大页面大小限制


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """书籍视图集，提供列表和详情的只读接口
    
    允许匿名用户访问，无需登录即可查看书籍列表和详情
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # 允许所有人访问（包括匿名用户）
    pagination_class = StandardPageNumberPagination  # 使用标准分页器，提高性能
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["created_at", "publication_year", "title", "author"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """列表时注解评分和评论统计"""
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.annotate(
                rating_count=Count("ratings"),
                rating_avg=Avg("ratings__score"),
                comment_count=Count("comments", distinct=True),
            )
        return qs
    
    def get_serializer_class(self):
        """列表使用精简序列化器，详情使用完整序列化器"""
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer


class AdminBookViewSet(viewsets.ModelViewSet):
    """管理员使用的书籍管理接口：支持增删改查，仅管理员可访问。

    路径示例：/api/books/admin/
    支持搜索：/api/books/admin/?search=关键词
    """

    queryset = Book.objects.all().order_by("-created_at")
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = LargePageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["created_at", "publication_year", "title", "author", "id"]
    ordering = ["-created_at"]
    
    def get_serializer_class(self):
        """列表使用精简序列化器，详情/创建/更新使用完整序列化器"""
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def book_rating_stats(request, book_id):
    """获取指定书籍的评分统计信息（豆瓣风格）。
    
    返回：
    - average_score: 平均分
    - total_ratings: 总评分人数
    - distribution: 1-5星的数量和百分比
    """
    
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found"}, status=404)
    
    ratings = Rating.objects.filter(book_id=book_id)
    total_count = ratings.count()
    
    if total_count == 0:
        return Response({
            "average_score": 0,
            "total_ratings": 0,
            "distribution": [
                {"star": 5, "count": 0, "percentage": 0},
                {"star": 4, "count": 0, "percentage": 0},
                {"star": 3, "count": 0, "percentage": 0},
                {"star": 2, "count": 0, "percentage": 0},
                {"star": 1, "count": 0, "percentage": 0},
            ]
        })
    
    # 计算平均分
    avg_score = ratings.aggregate(avg=Avg('score'))['avg'] or 0
    
    # 统计各星级数量
    star_counts = ratings.values('score').annotate(count=Count('score')).order_by('-score')
    star_dict = {item['score']: item['count'] for item in star_counts}
    
    # 构建分布数据（5星到1星）
    distribution = []
    for star in [5, 4, 3, 2, 1]:
        count = star_dict.get(star, 0)
        percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0
        distribution.append({
            "star": star,
            "count": count,
            "percentage": percentage
        })
    
    return Response({
        "average_score": round(avg_score, 1),
        "total_ratings": total_count,
        "distribution": distribution
    })
