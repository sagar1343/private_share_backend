from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, permissions, filters

from .models import Collection, PrivateFile, AccessLog, FilePermission
from .permissions import IsOwner
from .serializers import CollectionSerializer, UserSerializer, PrivateFileSerializer, AccessLogSerializer, \
    FilePermissionSerializer


class UserViewset(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all().only('id', 'email', 'profile_pic', 'first_name', 'last_name')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email']

    def get_permissions(self):
        return [permissions.AllowAny()] if self.action == 'list' else [IsOwner()]


class CollectionViewset(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user_pk = int(self.kwargs.get("user_pk", 0))
        if user_pk != self.request.user.id:
            raise PermissionDenied("You are not allowed to view this collection")
        return Collection.objects.filter(user=self.kwargs['user_pk'])


class PrivateFileViewset(viewsets.ModelViewSet):
    serializer_class = PrivateFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['collections']
    pagination_class = None

    def get_queryset(self):
        return PrivateFile.objects.filter(collections__user=self.request.user).prefetch_related('collections')


class FilePermissionViewset(viewsets.ModelViewSet):
    queryset = FilePermission.objects.all()
    serializer_class = FilePermissionSerializer


class AccessLogViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccessLogSerializer

    def get_queryset(self):
        return AccessLog.objects.filter(private_file_id=self.kwargs['file_pk']).select_related('user', 'private_file')
