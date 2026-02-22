from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include your accounts app URLs
    path('accounts/', include('accounts.urls')),

    # Include your recommender app URLs
    path('recommender/', include('recommender.urls')),

    path('emotion/', include('emotion_recognition.urls')),


    # Default root URL redirects to the login page
    path('', RedirectView.as_view(url=reverse_lazy('login'), permanent=False)),
]
