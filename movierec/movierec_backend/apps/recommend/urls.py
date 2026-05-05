from django.urls import path
from .views import (
    hot_books, 
    stats_overview, 
    user_recommendations, 
    similar_books, 
    hybrid_recommendations,
    wordcloud_data
)

urlpatterns = [
    path("hot/", hot_books, name="recommend-hot"),
    path("stats/", stats_overview, name="recommend-stats"),
    path("user/", user_recommendations, name="recommend-user"),
    path("similar/", similar_books, name="recommend-similar"),
    path("hybrid/", hybrid_recommendations, name="recommend-hybrid"),
    path("wordcloud/", wordcloud_data, name="recommend-wordcloud"),
]
