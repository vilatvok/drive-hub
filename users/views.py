from math import ceil

from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from jwt.exceptions import ExpiredSignatureError

from users import serializers, utils
from users.models import Achievement, Comment
from users.permissions import IsNotAuthenticated, IsUser
from users.tasks import get_activity_scheduler

from enterprises.serializers import CompanySerializer, CarServiceSerializer


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsUser]
    lookup_field = 'slug'

    def create(self, request, *args, **kwargs):
        """This method doesnt create user until user verificate email."""

        serializer = serializers.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = utils.create_register_token(**serializer.validated_data)
        utils.send_token_email(
            f'http://127.0.0.1:8000/email-verificate/{token}',
            serializer.validated_data['email'],
        )
        return Response({'status': 'Check email'})

    @action(detail=True, methods=['patch'], url_path='change-password')
    def change_password(self, request, slug=None):
        serializer = serializers.PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'status': 'changed'})

    @action(detail=True, methods=['get'])
    def passport(self, request, slug=None):
        user = self.get_object()
        data = user.passport if hasattr(user, 'passport') else []
        serializer = serializers.PassportSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-passport')
    def add_passport(self, request, slug=None):
        serializer = serializers.PassportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='get-achievements')
    def get_achievements(self, request, slug=None):
        data = self.get_object().achievements.all()
        serializer = serializers.UserAchievementSerializer(data, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='get-companies')
    def get_companies(self, request, slug=None):
        data = self.get_object().company_added.all()
        serializer = CompanySerializer(data, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='get-services')
    def get_services(self, request, slug=None):
        data = self.get_object().carservice_added.all()
        serializer = CarServiceSerializer(data, many=True, context={'request': request})
        return Response(serializer.data)


class CommentLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, *args, **kwargs):
        comment = Comment.objects.get(id=comment_id)
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
            comment.save()
            return Response({'status': 'error'}, status.HTTP_400_BAD_REQUEST)
        else:
            comment.likes.add(request.user)
            comment.save()
            return Response({'status': 'success'})
        

class CommentDeleteAPIView(DestroyAPIView):
    queryset = (
        Comment.objects.select_related('user').prefetch_related('likes')
    )
    serializer_class = serializers.CommentSerializer
    lookup_url_kwarg = 'comment_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == self.request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'status': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)


class EmailVerificateAPIView(APIView):
    permission_classes = [IsNotAuthenticated]

    def get(self, request, token):
        try:
            token = utils.get_register_token(token)
        except ExpiredSignatureError:
            return Response({'status': 'token is invalid'}, status.HTTP_400_BAD_REQUEST)
        else:
            user, created = User.objects.get_or_create(
                username=token['username'],
                email=token['email'],
                first_name=token['first_name'],
                last_name=token['last_name'],
                password=token['password'],
                phone=token['phone'],
            )
            if created:
                get_activity_scheduler(user.id, user.username, user.date_joined)
                return Response({'status': 'success'})
            return Response({'status': 'already created'}, status.HTTP_400_BAD_REQUEST)


class PasswordResetLinkAPIView(APIView):
    """Send one time link to email address."""

    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        serializer = serializers.PasswordResetLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
        except User.DoesNotExist:
            return Response(
                {'status': "User with such email doesn't exist"},
                status.HTTP_400_BAD_REQUEST,
            )
        else:
            uuid = urlsafe_base64_encode(force_bytes(user))
            token = default_token_generator.make_token(user)
            utils.send_token_email(
                f'http://127.0.0.1:8000/password_reset/{uuid}/{token}/',
                user.email
            )
            return Response({'status': 'The letter has been sent to your email'})


class PasswordResetAPIView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request, uidb64, token):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(username=user)
        valid = default_token_generator.check_token(user, token)
        if not valid:
            return Response({'status': 'Invalid token'}, status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'status': 'Changed'}, status.HTTP_200_OK)


class AchievementViewSet(ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = serializers.AchievementSerializer
    permission_classes = [IsAuthenticated]


class RouteAPIView(CreateAPIView):
    """Show the shortest way between two cities."""

    serializer_class = serializers.RouteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_ = serializer.validated_data['from_']
        where = serializer.validated_data['where']
        avg_speed = serializer.validated_data['avg_speed']

        shortest, km = utils.create_routes(from_, where)

        time_drive = round(km / avg_speed, 2)
        hours_drive = int(time_drive)
        minutes_drive = ceil(time_drive % 1 * 60)

        data = {
            'city': where,
            'shortest_way': shortest,
            'distance': km,
            f'time_drive ({avg_speed} km/h)': f'{hours_drive} hours {minutes_drive} minutes',
        }
        return Response(data)
