from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "profile_pic"]


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField()
