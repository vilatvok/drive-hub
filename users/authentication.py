from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class PhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_model()
        try:
            user = user.objects.get(phone=username)
            if user.check_password(password):
                return user
        except user.DoesNotExist:
            return

    def get_user(self, user_id):
        user = get_user_model().objects.get(id=user_id)
        try:
            return user
        except:
            return
