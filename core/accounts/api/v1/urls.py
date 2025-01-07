from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = "api-v1"
router = DefaultRouter()
router.register("auth", views.AuthUserViewSet, "auth")
urlpatterns = [
    path("jwt/create/", views.JWTCreateView.as_view(), name="jwt-create"),
    path("jwt/refresh/", views.JWTRefreshView.as_view(), name="jwt-refresh"),
    path(
        "token/login/",
        views.CustomTokenLoginView.as_view(),
        name="token-login",
    ),
    path(
        "token/logout/",
        views.CustomTokenLogoutView.as_view(),
        name="token-logout",
    ),
    path(
        "forget-password",
        views.ForgetPasswordView.as_view(),
        name="forget-password",
    ),
    path(
        "forget-password-confirm/<str:token>",
        views.ForgetPasswordConfirmView.as_view(),
        name="forget-password-confirm",
    ),
    path(
        "verify-account/<str:token>",
        views.VerifyAccountView.as_view(),
        name="verify-account",
    ),
    path(
        "verify-account/resend/",
        views.VerifyAccountResendView.as_view(),
        name="verify-account-resend",
    ),
]
urlpatterns += router.urls
