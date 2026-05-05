from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Rating, Comment

User = get_user_model()


class RatingUpsertSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    score = serializers.IntegerField(min_value=1, max_value=5)


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("id", "user", "book", "score", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")


class CommentCreateSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    content = serializers.CharField(min_length=1, max_length=2000)


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_score = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "book", "user", "username", "content", "created_at", "user_score")
        read_only_fields = ("id", "user", "username", "created_at", "user_score")
    
    def get_username(self, obj):
        """获取用户名，如果是MD5格式则生成友好名称"""
        if not obj.user:
            return "匿名用户"
        username = obj.user.username or ""
        # 检查是否为32位MD5哈希（豆瓣数据集的匿名用户）
        if len(username) == 32 and username.isalnum() and all(c in '0123456789abcdef' for c in username.lower()):
            return f"豆瓣用户_{username[:8]}"
        return username or "匿名用户"
    
    def get_user_score(self, obj):
        """获取该用户对该书的评分"""
        try:
            rating = Rating.objects.filter(user=obj.user, book=obj.book).first()
            return rating.score if rating else None
        except Exception:
            return None
