from datetime import datetime, timedelta, timezone

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.test import APITestCase

from users import serializers
from users.models import Achievement, UserAchievement, Comment
from users.utils import create_register_token
from enterprises.serializers import CompanySerializer, CarServiceSerializer
from enterprises.models import Company, CarService
from fuels.models import Fuel


User = get_user_model()


class UserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='hsdfb', password='34324', email='asda@gmail.com'
        )
        self.client.force_authenticate(self.user)
        self.ach = Achievement.objects.create(title='fas', description='sa', bonus=10)
        self.user_ach = UserAchievement.objects.create(user=self.user)

    def test_get(self):
        response = self.client.get(reverse('users-list'))
        serializer = serializers.UserSerializer(
            [self.user], 
            many=True, 
            context={'request': response.wsgi_request}
        )  
        self.assertEqual(response.data, serializer.data)

    def test_get_object(self):
        response = self.client.get(reverse('users-detail', args=[self.user.slug]))
        serializer = serializers.UserSerializer(
            self.user, context={'request': response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_create(self):
        data = {
            'username': 'taras',
            'email': 'gtrfh@gmail.com',
            'phone': '+380683456783',
            'first_name': 'asd',
            'last_name': 'astr',
            'password': '12345jaskd',
        }

        response = self.client.post(reverse('users-list'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_verification(self):
        self.client.logout()
        data = {
            'username': 'taras',
            'email': 'gtrfh@gmail.com',
            'phone': '+380683456783',
            'first_name': 'asd',
            'last_name': 'astr',
            'password': '12345jaskd',
        }
        token = create_register_token(**data)
        response = self.client.get(reverse('email_verificate', args=[token]))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(User.objects.filter(username='taras').exists())

    def test_change_password(self):
        data = {'password': '3728412grt'}

        response = self.client.patch(
            reverse('users-change-password', args=[self.user.slug]),
            data=data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('3728412grt'))

    def test_add_passport(self):
        current_time = datetime.now(timezone.utc)

        data = {
            'id_number': '542341239',
            'tax_number': '5423412340',
            'date_issue': current_time - timedelta(days=365),
            'date_expiry': current_time,
        }
        response = self.client.post(
            reverse('users-add-passport', args=[self.user.slug]),
            data=data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.passport)

    def test_password_reset_link(self):
        self.client.logout()
        data = {'email': 'asda@gmail.com'}
        response = self.client.post(reverse('password_reset_link'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        self.client.logout()
        uid = urlsafe_base64_encode(force_bytes(self.user))
        data = {'new_password': '1234f345ddd', 'confirm_password': '1234f345ddd'}
        token = default_token_generator.make_token(self.user)
        response = self.client.post(
            reverse('password_reset', args=[uid, token]),
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('1234f345ddd'))

    def test_get_achievements(self):
        response = self.client.get(
            reverse('users-get-achievements', args=[self.user.slug])
        )
        data = self.user.achievements.all()
        serializer = serializers.UserAchievementSerializer(data, many=True)
        self.assertEqual(response.data, serializer.data, response.data)

    def test_add_achievement(self):
        self.user_ach.user_achievement.add(self.ach)
        self.assertEqual(self.user_ach.user_achievement.all().count(), 1)

    def test_get_companies(self):
        response = self.client.get(
            reverse('users-get-companies', args=[self.user.slug])
        )
        c = self.user.company_added.all()
        serializer = CompanySerializer(
            c, many=True, context={'request': response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)

    def test_get_services(self):
        response = self.client.get(reverse('users-get-services', args=[self.user.slug]))
        c = self.user.carservice_added.all()
        serializer = CarServiceSerializer(
            c, many=True, context={'request': response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)


class RatingTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='admin', password='124312', email='sad'
        )
        self.client.force_authenticate(user)
        self.fuel = Fuel.objects.create(name='gas', price=51.00)
        company = Company.objects.create(
            slug='random-company',
            owner='John Doe',
            name='Random Car Service',
            created_date='2022-01-01',
            added_by=user,
            description='A random car service company for testing purposes.',
            phone_number='+380234567890',
            email='info@randomcarservice.com',
            website='http://randomcarservice.com',
            address='123 Main Street, Cityville',
            is_verified=True,
        )

        self.service = CarService.objects.create(
            company=company,
            industry='car wash',
            slug='random-com',
            owner='John Doe',
            name='Random C',
            created_date='2022-01-01',
            added_by=user,
            description='A random car service company for testi',
            phone_number='+380234567890',
            email='info@randomcarservice.com',
            address='123 Main Street, Cityville',
            is_verified=True,
        )

    def test_rate(self):
        data = {'rate': 5}

        response1 = self.client.post(
            reverse('fuel-rate', args=[self.fuel.slug]), data=data
        )
        response2 = self.client.post(
            reverse('service-rate', args=[self.service.slug]), data=data
        )

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_rate_update(self):
        data = {'rate': 5}

        response_1a = self.client.post(
            reverse('fuel-rate', args=[self.fuel.slug]), data=data
        )
        response_2a = self.client.post(
            reverse('service-rate', args=[self.service.slug]), data=data
        )

        data = {'rate': 4}
        response_1b = self.client.post(
            reverse('fuel-rate', args=[self.fuel.slug]), data=data
        )
        response_2b = self.client.post(
            reverse('service-rate', args=[self.service.slug]), data=data
        )

        # Check if user rated
        self.assertEqual(response_1a.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2a.status_code, status.HTTP_201_CREATED)
        
        # Check if rate changed
        self.assertEqual(response_1b.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2b.status_code, status.HTTP_200_OK)

        self.assertEqual(self.fuel.rating.all()[0].rate, 4)
        self.assertEqual(self.service.rating.all()[0].rate, 4)


class CommentTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='124312', email='sad'
        )
        self.client.force_authenticate(self.user)
        self.fuel = Fuel.objects.create(name='gas', price=51.00)
        self.comment = Comment.objects.create(
            user=self.user, comment_object=self.fuel, message='hello'
        )

        company = Company.objects.create(
            slug='random-company',
            owner='John Doe',
            name='Random Car Service',
            created_date='2022-01-01',
            added_by=self.user,
            description='A random car service company for testing purposes.',
            phone_number='+380234567890',
            email='info@randomcarservice.com',
            website='http://randomcarservice.com',
            address='123 Main Street, Cityville',
            is_verified=True,
        )

        self.service = CarService.objects.create(
            company=company,
            industry='car wash',
            slug='random-com',
            owner='John Doe',
            name='Random C',
            created_date='2022-01-01',
            added_by=self.user,
            description='A random car service company for testi',
            phone_number='+380234567890',
            email='info@randomcarservice.com',
            address='123 Main Street, Cityville',
            is_verified=True,
        )

        Comment.objects.create(
            user=self.user, comment_object=self.service, message='hello'
        )

    def test_add_comment(self):
        data = {
            'message': 'Very good',
        }

        response1 = self.client.post(
            reverse('fuel-add-comment', args=[self.fuel.slug]), 
            data=data, 
            format='json'
        )
        response2 = self.client.post(
            reverse('service-add-comment', args=[self.service.slug]),
            data=data,
            format='json',
        )

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.fuel.comments.all().count(), 2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.service.comments.all().count(), 2)

    def test_delete_comment(self):
        response = self.client.delete(reverse('delete_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.fuel.comments.all().count())

    def test_like_comment(self):
        response = self.client.post(reverse('like_comment', args=[self.comment.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.comment.likes.filter(id=self.user.id).exists())


class AchievementTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='1231'
        )
        self.client.force_authenticate(self.user)
        self.ach = Achievement.objects.create(title='fas', description='sa', bonus=10)

    def test_get(self):
        response = self.client.get(reverse('achievements-list'))
        serializer = serializers.AchievementSerializer([self.ach], many=True)
        self.assertEqual(response.data, serializer.data, response.data)


class RouteTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='hsdfb', password='34324'
        )
        self.client.force_authenticate(self.user)

    def test_route(self):
        data = {'from_': 'Lviv', 'where': 'Kyiv'}
        response = self.client.post(reverse('routes'), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
