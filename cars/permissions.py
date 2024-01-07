from rest_framework.permissions import BasePermission


class IsPassport(BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            try:
                return bool(request.user.passport)
            except:
                return False
        return True
