from django.contrib.auth import get_user_model, password_validation

from rest_framework import serializers

from users.utils import cities_
from users.models import Passport, Comment, Achievement, UserAchievement, Rating


User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='users-detail', lookup_field='slug', read_only=True
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'url',
            'username',
            'phone',
            'email',
            'first_name',
            'last_name',
            'password',
        ]
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate_password(self, value):
        password_validation.validate_password(value)
        return value
        
    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class UserCommentSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='users-detail', lookup_field='slug'
    )

    class Meta:
        model = User
        fields = ['url', 'username']


class CommentSerializer(serializers.ModelSerializer):
    user = UserCommentSerializer(read_only=True)
    likes = serializers.SerializerMethodField('get_likes', read_only=True)

    class Meta:
        model = Comment
        exclude = ['content_type', 'object_id']

    def get_likes(self, obj):
        return obj.likes.count()


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rate']


class PassportSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Passport
        fields = '__all__'


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    
    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordResetLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        password_validation.validate_password(data['new_password'])
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Password dont match')
        return data 


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    user_achievement = AchievementSerializer(many=True)

    class Meta:
        model = UserAchievement
        exclude = ['user']


class RouteSerializer(serializers.Serializer):
    from_ = serializers.ChoiceField(choices=cities_, required=False) 
    where = serializers.ChoiceField(choices=cities_)
    avg_speed = serializers.IntegerField(default=80, min_value=40, max_value=130)
