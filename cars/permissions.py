from rest_framework.permissions import BasePermission

from django.core.exceptions import ObjectDoesNotExist


class IsPassport(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            try:
                return bool(request.user.passport.is_verified)
            except ObjectDoesNotExist:
                return False
        return True
