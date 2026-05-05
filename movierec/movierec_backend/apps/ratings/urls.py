from django.urls import path
from . import views

urlpatterns = [
    path("rate/", views.rate_book, name="rate-book"),
    path("my-rating/", views.my_rating, name="my-rating"),
    path("my/ratings/", views.my_ratings, name="my-ratings"),
    path("my/comments/", views.my_comments, name="my-comments"),
    path("comments/", views.list_comments, name="list-comments"),
    path("comments/create/", views.create_comment, name="create-comment"),
]