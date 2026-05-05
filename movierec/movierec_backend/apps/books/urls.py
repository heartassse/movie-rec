from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AdminBookViewSet, book_rating_stats
from .image_proxy import image_proxy

router = DefaultRouter()
router.register(r"admin", AdminBookViewSet, basename="admin-book")
router.register(r"", BookViewSet, basename="book")

urlpatterns = [
    path("image-proxy/", image_proxy, name="image-proxy"),
    path("<int:book_id>/rating-stats/", book_rating_stats, name="book-rating-stats"),
    path("", include(router.urls)),
]
