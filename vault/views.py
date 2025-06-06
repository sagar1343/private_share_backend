from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, mixins, status
from rest_framework.response import Response

from .models import Collection, PrivateFile, AccessLog, FilePermission
from .permissions import IsOwner
from .serializers import CollectionSerializer, UserSerializer, PrivateFileSerializer, AccessLogSerializer, FilePermissionSerializer, FileShareSerializer
from .pagination import CustomPagination
from .utils import generate_url

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
    pagination_class = CustomPagination
    

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

    def get_queryset(self):
        return PrivateFile.objects.prefetch_related('collections').filter(Q(collections__user=self.request.user) & (Q(expiration_time__gt=timezone.now() - timezone.timedelta(days=7))| Q(expiration_time__isnull=True))).distinct()


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
        annotations = {
            f"sender_{field}": Subquery(Collection.objects.filter(privatefile=OuterRef('id')).values(f"user__{field}")[:1])
            for field in user_fields
        }
        return PrivateFile.objects.filter(file_permissions__allowed_users__contains=[self.request.user.email]).filter(Q(expiration_time__gt=timezone.now() - timezone.timedelta(days=7)) | Q(expiration_time__isnull=True)
        ).annotate(**annotations).distinct()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        file_permission = get_object_or_404(FilePermission, file=instance)

        if instance.expiration_time and instance.expiration_time < timezone.now():
            return Response({"message": "This file has expired"}, status=status.HTTP_403_FORBIDDEN)

        if not file_permission.has_access(self.request.user.email):
            return Response({"message": "You are not allowed to view this file"}, status=status.HTTP_403_FORBIDDEN)

        if instance.password and not instance.check_file_password(request.query_params.get("password")):
            return Response({"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)

        with transaction.atomic():
            private_file = PrivateFile.objects.get(id=instance.id)

            if private_file.download_count >= private_file.max_download_count:
                return Response({"message": "Download limit has been reached."}, status=status.HTTP_403_FORBIDDEN)

            private_file.download_count = F('download_count') + 1
            private_file.save()

            AccessLog.objects.create(private_file=instance, user=self.request.user, access_time=timezone.now())
            return Response(generate_url(instance.file.name))
