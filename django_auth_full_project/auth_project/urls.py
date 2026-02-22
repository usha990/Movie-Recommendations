from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('recommender/', include('recommender.urls')),
    path('', include('emotion_recognition.urls')),  # ✅ include emotion app URLs
    
]
