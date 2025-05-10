from django.contrib.auth import get_user_model
from rest_framework import serializers

from humanize import naturalsize

from .models import Collection, PrivateFile, AccessLog, FilePermission


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "profile_pic"]


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'user', 'created_at', 'updated_at']

    def validate_title(self, value):
        collection_exists = Collection.objects.filter(user=self.context['user'], title__iexact=value).exists()
        if collection_exists:
            raise serializers.ValidationError("Collection title is already in use.")
        return value


class PrivateFileSerializer(serializers.ModelSerializer):
    download_count = serializers.IntegerField(read_only=True)
    size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PrivateFile
        fields = ["id", "file", "file_name", "size", "password", "is_protected", "collections",
                  "expiration_time", "max_download_count",
                  "download_count", "created_at"]
    
    def get_is_protected (self, obj):
        return obj.is_protected()
    
    def get_size(self, obj):
        return naturalsize(obj.file.size)
    
    def validate_file(self, value):
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 100MB")
        return value

    def validate_collections(self, value):
        user = self.context["request"].user
        user_collection_ids = set(user.collection_set.values_list('id', flat=True))
        collection_ids = {collection.id for collection in value}
        if collection_ids.issubset(user_collection_ids):
            return value
        raise serializers.ValidationError("One or more collections does not exist for this user.")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop("password")
        return representation


class FilePermissionSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FilePermission
        fields = ['file', 'allowed_users']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['allowed_users'] = list(instance.allowed_users.values_list('email', flat=True))
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


class FileShareSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = PrivateFile
        fields = ['id', 'file_name', 'size', 'is_protected', 'sender']

    def get_size(self, obj):
        return naturalsize(obj.file.size)

    def get_sender(self, obj):
        return {
            'email': obj.sender_email,
            'profile_pic': obj.sender_profile_pic,
            'first_name': obj.sender_first_name,
            'last_name': obj.sender_last_name
        }