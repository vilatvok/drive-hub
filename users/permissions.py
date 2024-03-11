from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        return False


class IsUser(BasePermission):
    def has_permission(self, request, view):
        if request.method not in ['POST', 'OPTIONS']:
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in [
            'update',
            'partial_update',
            'destroy',
            'change_password',
            'add_passport',
            'passport'
        ]:
            return request.user == obj
        return True
