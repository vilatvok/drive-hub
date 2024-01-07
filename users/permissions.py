from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["POST", "OPTIONS"]:
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in [
            "update",
            "partial_update",
            "destroy",
            "password_change",
            "add_passport",
        ]:
            return request.user == obj
        return True
