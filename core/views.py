from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import verify_google_token, generate_token_pair
from .models import User
from .serializers import UserSerializer, GoogleLoginSerializer


# Create your views here.
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = get_user_model().objects.only('id', 'email', 'first_name', 'last_name', 'profile_pic')
        user = get_object_or_404(queryset, id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class GoogleLoginView(ListCreateAPIView):
    queryset = User.objects.all()

    def get_permissions(self):
        return [IsAdminUser()] if self.request.method == "GET" else [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        elif self.request.method == "POST":
            return GoogleLoginSerializer

    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        response = verify_google_token(token)
        if not response:
            return Response(
                data={"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        email = response.get("email")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": response.get("given_name"),
                "last_name": response.get("family_name"),
                "profile_pic": response.get("picture"),
            },
        )
        if created:
            user.set_password(None)
            user.save()

        access_token, refresh_token = generate_token_pair(user)
        return Response({"access": access_token, "refresh": refresh_token})
