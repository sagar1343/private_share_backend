from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, OuterRef, Subquery
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, mixins, status
from rest_framework.response import Response

from .models import Collection, PrivateFile, AccessLog, FilePermission
from .permissions import IsOwner
from .serializers import CollectionSerializer, UserSerializer, PrivateFileSerializer, AccessLogSerializer, FilePermissionSerializer, FileShareSerializer


class UserViewset(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all().only('id', 'email', 'profile_pic', 'first_name', 'last_name')
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email']
    pagination_class = None

    def get_permissions(self):
        return [permissions.IsAuthenticated()] if self.action == 'list' else [IsOwner()]


class CollectionViewset(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user_pk = int(self.kwargs.get('user_pk', 0))
        if user_pk != self.request.user.id:
            raise PermissionDenied("You are not allowed to view this collection")
        return Collection.objects.filter(user=self.kwargs['user_pk']).order_by('-created_at')

    def get_serializer_context(self):
        return {'user': self.request.user}


class PrivateFileViewset(viewsets.ModelViewSet):
    serializer_class = PrivateFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['collections']
    pagination_class = None

    def get_queryset(self):
        return PrivateFile.objects.prefetch_related('collections').filter(collections__user=self.request.user).distinct()


class FilePermissionViewset(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = FilePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        file_pk = self.kwargs.get('file_pk')
        return get_object_or_404(FilePermission, file_id=file_pk)


class AccessLogViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccessLogSerializer

    def get_queryset(self):
        return AccessLog.objects.filter(private_file_id=self.kwargs['file_pk']).select_related('user', 'private_file')


class FileShareViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FileShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_fields = ['email', 'profile_pic', 'first_name', 'last_name']
        annotations= {
            f"sender_{field}" : Subquery(Collection.objects.filter(privatefile=OuterRef('id')).values(f"user__{field}")[:1])
            for field in user_fields
        }
        return PrivateFile.objects.filter(file_permissions__allowed_users=self.request.user).annotate(**annotations)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file_permisssion = get_object_or_404(FilePermission, file=instance.id)

        if instance.expiration_time and instance.expiration_time < timezone.now():
            return Response({"message": "This file has expired"}, status=status.HTTP_403_FORBIDDEN)

        if not file_permisssion.allowed_users.filter(id=self.request.user.id).exists():
            return Response({"message": "You are not allowed to view this file"}, status=status.HTTP_403_FORBIDDEN)

        if instance.password and not instance.check_file_password(request.data.get("password")):
            return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        with transaction.atomic():
            private_file = PrivateFile.objects.get(id=instance.id)

            if private_file.download_count >= private_file.max_download_count:
                return Response({"message": "Download limit has been reached."}, status=status.HTTP_403_FORBIDDEN)

            private_file.download_count = F('download_count') + 1
            private_file.save()

            AccessLog.objects.create(private_file=instance, user=self.request.user, access_time=timezone.now())
            return FileResponse(instance.file, as_attachment=True)
