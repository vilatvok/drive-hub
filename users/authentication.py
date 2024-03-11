from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


User = get_user_model()


class PhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User
        try:
            user = user.objects.get(phone=username)
            if user.check_password(password):
                return user
        except user.DoesNotExist:
            return None

    def get_user(self, user_id):
        user = User.objects.get(id=user_id)
        try:
            return user
        except:
            return None
