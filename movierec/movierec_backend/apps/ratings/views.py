from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.books.models import Book

from .models import Rating, Comment
from .serializers import (
    RatingUpsertSerializer,
    RatingSerializer,
    CommentCreateSerializer,
    CommentSerializer,
)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def rate_book(request):
    """对书籍评分：同一用户同一本书再次评分会覆盖（upsert）。"""

    ser = RatingUpsertSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    book = get_object_or_404(Book, id=ser.validated_data["book_id"])
    score = ser.validated_data["score"]

    with transaction.atomic():
        rating, _created = Rating.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={"score": score},
        )

    return Response(RatingSerializer(rating).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_rating(request):
    """获取我对某本书的评分（用于前端回显）。"""

    book_id = request.query_params.get("book_id")
    if not book_id:
        return Response({"detail": "book_id is required"}, status=400)

    rating = Rating.objects.filter(user=request.user, book_id=book_id).first()
    if not rating:
        return Response({"score": None})

    return Response({"score": rating.score})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def list_comments(request):
    """按书籍获取评论列表（含用户评分）。"""

    book_id = request.query_params.get("book_id")
    if not book_id:
        return Response({"detail": "book_id is required"}, status=400)

    qs = Comment.objects.filter(book_id=book_id).select_related("user").order_by("-created_at")

    try:
        page = int(request.query_params.get("page", "1"))
        page_size = int(request.query_params.get("page_size", "10"))
    except ValueError:
        return Response({"detail": "page/page_size must be int"}, status=400)

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 50:
        page_size = 50

    start = (page - 1) * page_size
    end = start + page_size
    items = list(qs[start:end])

    # 预加载该书所有评论用户的评分（避免 N+1 查询）
    user_ids = [c.user_id for c in items]
    ratings_map = {}
    if user_ids:
        ratings = Rating.objects.filter(book_id=book_id, user_id__in=user_ids).values('user_id', 'score')
        ratings_map = {r['user_id']: r['score'] for r in ratings}

    # 手动构建结果，附加评分
    results = []
    for comment in items:
        data = CommentSerializer(comment).data
        data['user_score'] = ratings_map.get(comment.user_id)
        results.append(data)

    return Response(
        {
            "count": qs.count(),
            "page": page,
            "page_size": page_size,
            "results": results,
        }
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_comment(request):
    """发表评论。"""

    ser = CommentCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    book = get_object_or_404(Book, id=ser.validated_data["book_id"])
    comment = Comment.objects.create(
        user=request.user,
        book=book,
        content=ser.validated_data["content"],
    )

    return Response(CommentSerializer(comment).data, status=201)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_ratings(request):
    """我的评分列表（用于个人中心）。"""

    qs = (
        Rating.objects.filter(user=request.user)
        .select_related("book")
        .order_by("-updated_at", "-id")
    )

    try:
        limit = int(request.query_params.get("limit", "50"))
    except ValueError:
        limit = 50
    if limit < 1:
        limit = 50
    if limit > 200:
        limit = 200

    items = [
        {
            "book_id": r.book_id,
            "title": r.book.title,
            "score": r.score,
            "updated_at": r.updated_at,
        }
        for r in qs[:limit]
    ]
    return Response({"limit": limit, "results": items})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_comments(request):
    """我的评论列表（用于个人中心）。"""

    qs = (
        Comment.objects.filter(user=request.user)
        .select_related("book")
        .order_by("-created_at", "-id")
    )

    try:
        limit = int(request.query_params.get("limit", "50"))
    except ValueError:
        limit = 50
    if limit < 1:
        limit = 50
    if limit > 200:
        limit = 200

    items = [
        {
            "id": c.id,
            "book_id": c.book_id,
            "title": c.book.title,
            "content": c.content,
            "created_at": c.created_at,
        }
        for c in qs[:limit]
    ]
    return Response({"limit": limit, "results": items})