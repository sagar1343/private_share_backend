from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'user', None)
        return owner == request.user if owner else obj == request.user
