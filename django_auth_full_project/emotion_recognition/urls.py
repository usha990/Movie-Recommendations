from django.urls import path
from . import views

urlpatterns = [
    path('emotion_page/', views.emotion_page, name='emotion_page'),
    path('detect_emotion/', views.detect_emotion, name='detect_emotion'),
    path('recommend_by_emotion/<str:emotion>/', views.recommend_by_emotion, name='recommend_by_emotion'),
]
