# recommender/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ui_view, name='reco_ui'),
    path('netflix/', views.netflix_style, name='netflix_style'),
    path('api/recommend/<int:user_id>/', views.recommend_api, name='reco_api'),
    path('api/<int:user_id>/', views.recommend_api, name='reco_api_alt'),
    path('search/', views.search_api, name='reco_search'),
    path('recommend_by_emotion/<str:emotion>/', views.recommend_by_emotion, name='recommend_by_emotion'),
]
