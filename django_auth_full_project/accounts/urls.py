
from django.urls import path
from . import views

from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('recommender/', include('recommender.urls')),  # ✅ Add this line
]


# urlpatterns = [
#     path('', views.home_view, name='home'),
#     path('register/', views.register_view, name='register'),
#     path('send-otp/',views.send_otp_view, name='send_otp'),
#     path('email-verification/<int:user_id>/',views.email_verification_view,name='email_verification'),
#     path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
#     path('login/', views.login_view, name='login'),
#      path('password-reset/', 
#          auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
#          name='password_reset'),

#     path('password-reset/done/', 
#          auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
#          name='password_reset_done'),

#     path('reset/<uidb64>/<token>/', 
#          auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
#          name='password_reset_confirm'),

#     path('reset/done/', 
#          auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
#          name='password_reset_complete'),
# ]
# ]
#     path('logout/', views.logout_view, name='logout'),
    

#     path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
#     path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
#     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
# ]
urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Email verification
    path('email-verification/<int:user_id>/', views.email_verification_view, name='email_verification'),
    path('send-otp/', views.send_otp_view, name='send_otp'),

    # Password reset flow
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), 
         name='password_reset_complete'),


         path('recommend/', views.recommend_view, name='recommend_view'),
]
urlpatterns += [
    path('recommend/<int:user_id>/', views.recommend_view, name='recommend'),
]
