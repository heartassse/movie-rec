from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """书籍序列化器（完整信息）"""
    class Meta:
        model = Book
        fields = '__all__'


class BookWithStatsSerializer(serializers.ModelSerializer):
    """书籍序列化器（含评分/评论统计，用于列表和推荐接口）"""
    rating_avg = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()  # 别名，兼容前端

    class Meta:
        model = Book
        fields = '__all__'

    def get_rating_avg(self, obj):
        avg = getattr(obj, 'rating_avg', None)
        if avg is not None:
            return round(float(avg), 1)
        return None

    def get_rating_count(self, obj):
        return getattr(obj, 'rating_count', None)

    def get_comment_count(self, obj):
        return getattr(obj, 'comment_count', None)

    def get_avg_rating(self, obj):
        return self.get_rating_avg(obj)


class BookListSerializer(serializers.ModelSerializer):
    """书籍列表序列化器（精简版，用于列表展示）"""
    description_preview = serializers.SerializerMethodField()
    rating_avg = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'cover_url', 'publication_year', 'isbn', 'created_at', 'description_preview',
                  'rating_avg', 'rating_count', 'comment_count']

    def get_description_preview(self, obj):
        """返回简介的前100个字符"""
        if obj.description:
            return obj.description[:100] + ('...' if len(obj.description) > 100 else '')
        return ''

    def get_rating_avg(self, obj):
        avg = getattr(obj, 'rating_avg', None)
        if avg is not None:
            return round(float(avg), 1)
        return None

    def get_rating_count(self, obj):
        return getattr(obj, 'rating_count', None)

    def get_comment_count(self, obj):
        return getattr(obj, 'comment_count', None)
