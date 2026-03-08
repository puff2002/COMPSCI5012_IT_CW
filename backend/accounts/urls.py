from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminLoginView,
    AdminRegisterView,
    LogoutView,
    MeView,
    UserLoginView,
    UserRegisterView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("user/register/", UserRegisterView.as_view(), name="user_register"),
    path("user/login/", UserLoginView.as_view(), name="user_login"),
    path("admin/register/", AdminRegisterView.as_view(), name="admin_register"),
    path("admin/login/", AdminLoginView.as_view(), name="admin_login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]
