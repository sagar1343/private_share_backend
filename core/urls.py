from django.urls import path

from core.views import GoogleLoginView

urlpatterns = [
    path("google-login/", GoogleLoginView.as_view(), name='google-login')
]
