from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # Parol tiklash (Django built-in)
    path('password-reset/',         auth_views.PasswordResetView.as_view(
        extra_email_context={'site_name': 'AvtoBaholash'}), name='password_reset'),
    path('password-reset/done/',    auth_views.PasswordResetDoneView.as_view(),    name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/',             auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]