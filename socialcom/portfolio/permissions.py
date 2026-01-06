from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow read-only access to anyone, but write access only to the object owner."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return getattr(obj, 'user', None) == request.user
