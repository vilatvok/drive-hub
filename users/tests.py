import requests

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from datetime import datetime, timedelta, timezone

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken

from fuel_store.models import Fuel
from enterprises.models import Company, CarService

from .serializers import *
from .models import Achievement, UserAchievement
from .utils import create_register_token

from enterprises.serializers import CompanySerializer, CarServiceSerializer


class UserTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="hsdfb", password="34324", email="asda@gmail.com"
        )
        self.client.force_authenticate(self.user)
        self.ach = Achievement.objects.create(title="fas", description="sa", bonus=10)
        self.user_ach = UserAchievement.objects.create(user=self.user)

    def test_get(self):
        response = self.client.get(reverse("users-detail", args=[self.user.slug]))

        url = requests.get(f"http://ip-api.com/json/185.204.71.251")
        ip = url.json()
        data = {
            "ip": ip.get("query"),
            "country": ip.get("country"),
            "city": ip.get("city"),
        }

        result = {"user": self.user, "location": data}
        serializer = UserInfoSerializer(
            result, context={"request": response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_create(self):
        data = {
            "username": "taras",
            "email": "gtrfh@gmail.com",
            "phone": "+380683456783",
            "first_name": "asd",
            "last_name": "astr",
            "password": "12345jaskd",
        }

        response = self.client.post(reverse("users-list"), data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_email_verification(self):
        data = {
            "username": "taras",
            "email": "gtrfh@gmail.com",
            "phone": "+380683456783",
            "first_name": "asd",
            "last_name": "astr",
            "password": "12345jaskd",
        }
        token = create_register_token(**data)
        response = self.client.get(reverse("email_verificate", args=[token]))
        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        self.assertTrue(get_user_model().objects.filter(username="taras").exists())

    def test_change_pswd(self):
        data = {"password": "3728412"}

        response = self.client.patch(
            reverse("users-password-change", args=[self.user.slug]),
            data=data,
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("3728412"))

    def test_add_passport(self):
        current_time = datetime.now(timezone.utc)

        data = {
            "id_number": "542341239",
            "tax_number": "5423412340",
            "date_issue": current_time - timedelta(days=365),
            "date_expiry": current_time,
        }
        response = self.client.post(
            reverse("users-add-passport", args=[self.user.slug]),
            data=data,
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.passport)

    def test_password_reset_send(self):
        data = {"email": "asda@gmail.com"}
        response = self.client.post(reverse("password_reset_send"), data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_password_reset(self):
        uid = urlsafe_base64_encode(force_bytes(self.user))
        data = {"new_password": "1234", "confirm_password": "1234"}
        token = RefreshToken.for_user(self.user).access_token
        response = self.client.post(
            reverse("password_reset", args=[uid, token]),
            data=data,
        )
        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("1234"))

    def test_get_achievements(self):
        response = self.client.get(
            reverse("users-get-achievements", args=[self.user.slug])
        )
        data = self.user.achievements.all()
        serializer = UserAchievementSerializer(data, many=True)
        self.assertEqual(response.data, serializer.data, response.data)

    def test_add_achievement(self):
        self.user_ach.user_achievement.add(self.ach)
        self.assertEqual(self.user_ach.user_achievement.all().count(), 1)

    def test_get_companies(self):
        response = self.client.get(
            reverse("users-get-companies", args=[self.user.slug])
        )
        c = self.user.company_added.all()
        serializer = CompanySerializer(
            c, many=True, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)

    def test_get_services(self):
        response = self.client.get(reverse("users-get-services", args=[self.user.slug]))
        c = self.user.carservice_added.all()
        serializer = CarServiceSerializer(
            c, many=True, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)


class RatingTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="admin", password="124312", email="sad"
        )
        self.client.force_authenticate(user)
        self.fuel = Fuel.objects.create(name="gas", price=51.00)
        company = Company.objects.create(
            slug="random-company",
            owner="John Doe",
            name="Random Car Service",
            created_date="2022-01-01",
            added_by=user,
            description="A random car service company for testing purposes.",
            phone_number="+380234567890",
            email="info@randomcarservice.com",
            website="http://randomcarservice.com",
            address="123 Main Street, Cityville",
            is_verified=True,
        )

        self.service = CarService.objects.create(
            company=company,
            industry="car wash",
            slug="random-com",
            owner="John Doe",
            name="Random C",
            created_date="2022-01-01",
            added_by=user,
            description="A random car service company for testi",
            phone_number="+380234567890",
            email="info@randomcarservice.com",
            address="123 Main Street, Cityville",
            is_verified=True,
        )

    def test_rate(self):
        data = {"rate": 5}

        response1 = self.client.post(
            reverse("fuel-rate", args=[self.fuel.slug]), data=data
        )
        response2 = self.client.post(
            reverse("service-rate", args=[self.service.slug]), data=data
        )

        self.assertEqual(response1.status_code, HTTP_201_CREATED)
        self.assertEqual(response2.status_code, HTTP_201_CREATED)

    def test_rate_update(self):
        data = {"rate": 5}

        response_1a = self.client.post(
            reverse("fuel-rate", args=[self.fuel.slug]), data=data
        )
        response_2a = self.client.post(
            reverse("service-rate", args=[self.service.slug]), data=data
        )

        data = {"rate": 4}
        response_1b = self.client.post(
            reverse("fuel-rate", args=[self.fuel.slug]), data=data
        )
        response_2b = self.client.post(
            reverse("service-rate", args=[self.service.slug]), data=data
        )

        # Check if user rated
        self.assertEqual(response_1a.status_code, HTTP_201_CREATED)
        self.assertEqual(response_2a.status_code, HTTP_201_CREATED)
        # Check if rate changed
        self.assertEqual(response_1b.status_code, HTTP_200_OK)
        self.assertEqual(response_2b.status_code, HTTP_200_OK)

        self.assertEqual(self.fuel.rating.all()[0].rate, 4)
        self.assertEqual(self.service.rating.all()[0].rate, 4)


class CommentTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin", password="124312", email="sad"
        )
        self.client.force_authenticate(self.user)
        self.fuel = Fuel.objects.create(name="gas", price=51.00)
        self.comment = Comment.objects.create(
            user=self.user, comment_object=self.fuel, message="hello"
        )

        company = Company.objects.create(
            slug="random-company",
            owner="John Doe",
            name="Random Car Service",
            created_date="2022-01-01",
            added_by=self.user,
            description="A random car service company for testing purposes.",
            phone_number="+380234567890",
            email="info@randomcarservice.com",
            website="http://randomcarservice.com",
            address="123 Main Street, Cityville",
            is_verified=True,
        )

        self.service = CarService.objects.create(
            company=company,
            industry="car wash",
            slug="random-com",
            owner="John Doe",
            name="Random C",
            created_date="2022-01-01",
            added_by=self.user,
            description="A random car service company for testi",
            phone_number="+380234567890",
            email="info@randomcarservice.com",
            address="123 Main Street, Cityville",
            is_verified=True,
        )

        Comment.objects.create(
            user=self.user, comment_object=self.service, message="hello"
        )

    def test_comment_add(self):
        data = {
            "message": "Very good",
        }

        response1 = self.client.post(
            reverse("fuel-comment", args=[self.fuel.slug]), data=data, format="json"
        )
        response2 = self.client.post(
            reverse("service-comment", args=[self.service.slug]),
            data=data,
            format="json",
        )

        self.assertEqual(response1.status_code, HTTP_201_CREATED)
        self.assertEqual(self.fuel.comment.all().count(), 2)
        self.assertEqual(response2.status_code, HTTP_201_CREATED)
        self.assertEqual(self.service.comment.all().count(), 2)

    def test_like_comment(self):
        response = self.client.post(reverse("like_comment", args=[self.comment.id]))
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(self.comment.likes.filter(id=self.user.id).exists())


class AchievementTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin", password="1231"
        )
        self.client.force_authenticate(self.user)
        self.ach = Achievement.objects.create(title="fas", description="sa", bonus=10)

    def test_get(self):
        response = self.client.get(reverse("achievements-list"))
        serializer = AchievementSerializer([self.ach], many=True)
        self.assertEqual(response.data, serializer.data, response.data)


class RoadTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="hsdfb", password="34324"
        )
        self.client.force_authenticate(self.user)

    def test_road(self):
        data = {"city": "Kyiv"}
        response = self.client.post(reverse("road"), data=data, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)
