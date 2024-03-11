from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    slug = models.SlugField(unique=True, max_length=180, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to='users/', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        return super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField('User', related_name='likes_comment', blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    comment_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.user} - {self.message}'


class Rating(models.Model):
    RATE_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='rating')
    rate = models.IntegerField(choices=RATE_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    rating_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.user} rate {self.rate} - {self.rating_object.name}'


class Passport(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='passport'
    )
    id_number = models.CharField(
        unique=True, validators=[MinLengthValidator(9), MaxLengthValidator(9)]
    )
    tax_number = models.CharField(
        unique=True, validators=[MinLengthValidator(10), MaxLengthValidator(10)]
    )
    date_issue = models.DateTimeField()
    date_expiry = models.DateTimeField()
    is_verified = models.BooleanField(default=False)


class Achievement(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    bonus = models.IntegerField()

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='achievements'
    )
    user_achievement = models.ManyToManyField(
        Achievement, related_name='user_achievements'
    )
    date_achievement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_username()