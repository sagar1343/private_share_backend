from django.urls import path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import GoogleLoginView, ProfileView

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/index.html")),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ProfileView.as_view(), name="user-profile"),
]
