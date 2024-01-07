import requests

from math import ceil

from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from jwt.exceptions import ExpiredSignatureError

from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from .models import Achievement
from .permissions import IsNotAuthenticated, IsUser
from .serializers import *
from .utils import create_roads, send_token_email, get_register_token, create_register_token
from enterprises.serializers import CompanySerializer, CarServiceSerializer


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [IsUser]
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        url = requests.get(f"http://ip-api.com/json/185.204.71.251")
        ip = url.json()
        data = {
            "ip": ip.get("query"),
            "country": ip.get("country"),
            "city": ip.get("city"),
        }
        instance = self.get_object()

        result = {"user": instance, "location": data}
        serializer = self.get_serializer(result)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = create_register_token(**serializer.validated_data)
        send_token_email(
            "http://127.0.0.1:8000/email_verificate/",
            token,
            email=serializer.validated_data["email"],
        )
        return Response({"status": "Check email"})

    @action(detail=True, methods=["patch"])
    def password_change(self, request, slug=None):
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data["password"])
            user.save()
            return Response({"status": "changed"})
        return Response({"status": "error"}, status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def add_passport(self, request, slug=None):
        serializer = PassportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def get_achievements(self, request, slug=None):
        data = self.get_object().achievements.all()
        serializer = UserAchievementSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def get_companies(self, request, slug=None):
        data = self.get_object().company_added.all()
        serializer = CompanySerializer(data, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def get_services(self, request, slug=None):
        data = self.get_object().carservice_added.all()
        serializer = CarServiceSerializer(data, many=True, context={"request": request})
        return Response(serializer.data)


# activate user if email verificate success
class EmailVerificateView(APIView):
    permission_classes = [IsNotAuthenticated]

    def get(self, request, token):
        try:
            t = get_register_token(token)
            del t["exp"]
            user, created = get_user_model().objects.get_or_create(
                username=t["username"],
                email=t["email"],
                first_name=t["first_name"],
                last_name=t["last_name"],
                password=t["password"],
                phone=t["phone"],
            )
            if created:
                return Response({"status": "success"})
            return Response({"status": "already created"}, status=HTTP_400_BAD_REQUEST)
        except ExpiredSignatureError:
            return Response({"status": "token is invalid"}, status=HTTP_400_BAD_REQUEST)


# send one time page to user for reset password
class PasswordResetSendView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        serializer = PasswordResetSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = get_user_model().objects.get(
                email=serializer.validated_data["email"]
            )
            token = RefreshToken.for_user(user).access_token
            send_token_email("http://127.0.0.1:8000/password_reset/", token, user=user)
            return Response({"status": "The letter has been sent to your email"})
        except get_user_model().DoesNotExist:
            return Response(
                {"status": "User with such email doesnt exist"},
                status=HTTP_400_BAD_REQUEST,
            )


# reset password user
class PasswordResetView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request, uidb64, token):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(username=user)
        try:
            AccessToken(token)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"status": "success"})
        except TokenError:
            return Response({"status": "token is invalid"}, status=HTTP_400_BAD_REQUEST)


class AchievementViewSet(ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]


# show the shortest way between the cities
class RoadView(CreateAPIView):
    serializer_class = RoadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RoadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # user_ip = get_client_ip_address(request)
        url = requests.get(f"http://ip-api.com/json/185.204.71.251")

        my_city = url.json()
        city = serializer.validated_data["city"]
        avg_speed = serializer.validated_data["avg_speed"]

        shortest, km = create_roads(my_city.get("city"), city)

        time_drive = round(km / avg_speed, 2)
        hours_drive = int(time_drive)
        minutes_drive = ceil(time_drive % 1 * 60)

        data = {
            "city": city,
            "shortest_way": shortest,
            "distance": km,
            f"time_drive ({avg_speed} km/h)": f"{hours_drive} hours {minutes_drive} minutes",
        }
        return Response(data)
