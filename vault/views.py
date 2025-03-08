from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, mixins, status
from rest_framework.response import Response

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
        return [permissions.IsAuthenticated()] if self.action == 'list' else [IsOwner()]


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
        return (PrivateFile.objects
                .filter(collections__user=self.request.user)
                .prefetch_related('collections')
                .distinct())


class FilePermissionViewset(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = FilePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        file_pk = self.kwargs.get('file_pk')
        return get_object_or_404(FilePermission, file_id=file_pk)


class AccessLogViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccessLogSerializer

    def get_queryset(self):
        return AccessLog.objects.filter(private_file_id=self.kwargs['file_pk']).select_related('user', 'private_file')


class FileShareViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PrivateFile.objects.all()
    serializer_class = PrivateFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file_permisssion = get_object_or_404(FilePermission, file=instance.id)
        if instance.expiration_time < timezone.now():
            return Response({"message": "You are not allowed to view this file"}, status=status.HTTP_403_FORBIDDEN)

        if file_permisssion.viewers.filter(id=self.request.user.id).exists():
            instance.file.open('rb')
            response = FileResponse(instance.file)
            response['Content-Disposition'] = f'inline; filename="{instance.file.name}"'
            return response
        if file_permisssion.downloaders.filter(id=self.request.user.id).exists():
            instance.file.open('rb')
            return FileResponse(instance, as_attachment=True)
        return Response({"message": "You are not allowed to view this file"}, status=status.HTTP_403_FORBIDDEN)
