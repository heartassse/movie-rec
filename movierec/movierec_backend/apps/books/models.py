from django.db import models

class Book(models.Model):
    """书籍模型"""
    title = models.CharField(max_length=200, verbose_name="书名")
    author = models.CharField(max_length=100, verbose_name="作者")
    description = models.TextField(blank=True, null=True, verbose_name="简介")
    cover_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="封面链接")
    publication_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="出版年份")
    isbn = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="ISBN")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "书籍"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title
