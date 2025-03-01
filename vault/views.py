from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, permissions

from .models import Collection
from .permissions import IsOwner
from .serializers import CollectionSerializer, UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        else:
            return [permissions.IsAuthenticated(), IsOwner()]


class CollectionViewset(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_pk = int(self.kwargs.get("user_pk", 0))
        if user_pk != self.request.user.id:
            raise PermissionDenied("You are not allowed to view this collection")
        return Collection.objects.filter(user=self.kwargs['user_pk'])
