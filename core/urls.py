from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import GoogleLoginView, ProfileView

urlpatterns = [
    path("google-login/", GoogleLoginView.as_view(), name='google-login'),
    path("refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', ProfileView.as_view(), name='user-profile'),
]
