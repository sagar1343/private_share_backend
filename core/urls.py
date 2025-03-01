from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import GoogleLoginView

urlpatterns = [
    path("google-login/", GoogleLoginView.as_view(), name='google-login'),
    path("refresh/", TokenRefreshView.as_view(), name='token_refresh'),
]
