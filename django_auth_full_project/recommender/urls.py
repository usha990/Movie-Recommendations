# recommender/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ui_view, name='reco_ui'),
    path('api/<int:user_id>/', views.recommend_api, name='reco_api'),
    path('search/', views.search_api, name='reco_search'),
]
