from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.response import Response

from core.utils import verify_google_token, generate_token_pair
from .models import User
from .serializers import UserSerializer, GoogleLoginSerializer


# Create your views here.
class GoogleLoginView(ListCreateAPIView, GenericAPIView):
    queryset = User.objects.all()
    permission_classes = []

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        elif self.request.method == "POST":
            return GoogleLoginSerializer

    def post(self, request):
        token = request.data.get("token")
        response = verify_google_token(token)
        if not response:
            return Response(data={'error': "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        email = response.get("email")
        first_name = response.get("given_name")
        last_name = response.get("family_name")
        profile_pic = response.get("picture")
        user, created = User.objects.get_or_create(email=email,
                                                   defaults={

                                                       "first_name": first_name,
                                                       "last_name": last_name,
                                                       "profile_pic": profile_pic})
        if created:
            user.set_password(None)
            user.save()

        [access_token, refresh_token] = generate_token_pair(user)
        return Response({'access_token': str(access_token), 'refresh_token': str(refresh_token)})
