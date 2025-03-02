from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Collection, PrivateFile, AccessLog, FilePermission


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "profile_pic"]


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'user_id', 'created_at', 'updated_at']


class PrivateFileSerializer(serializers.ModelSerializer):
    download_count = serializers.IntegerField(read_only=True)
    collections = serializers.SerializerMethodField()

    class Meta:
        model = PrivateFile
        fields = ["id", "file", "file_name", "collections", "expiration_time", "max_download_count", "download_count",
                  "created_at"]

    def get_collections(self, obj):
        return [collection.title for collection in obj.collections.all()]

    def validate_file(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 5MB")
        return value

    def validate_collection(self, value):
        user = self.context["request"].user
        user_collection = user.collection_set.values_list('id', flat=True)
        if value in user_collection:
            return value
        raise serializers.ValidationError("Collection does not exist")


class FilePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilePermission
        fields = ['file', 'viewers', 'downloaders']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['viewers'] = list(instance.viewers.values_list('email', flat=True))
        representation['downloaders'] = list(instance.downloaders.values_list('email', flat=True))
        return representation


class AccessLogSerializer(serializers.ModelSerializer):
    private_file = serializers.SerializerMethodField()
    access_by = serializers.SerializerMethodField()

    class Meta:
        model = AccessLog
        fields = ['id', 'private_file', 'access_by', 'access_time']

    def get_private_file(self, obj):
        return obj.private_file.file_name

    def get_access_by(self, obj):
        return obj.user.email
