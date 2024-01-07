from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT

from users.models import Comment, Rating
from users.serializers import CommentSerializer

from .models import Company, CarService
from .serializers import CompanySerializer, CarServiceSerializer


class CompanyTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="admin", password="124312", email="sad"
        )
        user2 = get_user_model().objects.create_user(username="admi", password="124312")
        self.client.force_authenticate(user)
        self.company = Company.objects.create(
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

    def test_get(self):
        response = self.client.get(reverse("company-list"))
        serializer = CompanySerializer(
            [self.company], many=True, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)

    def test_retrieve(self):
        response = self.client.get(reverse("company-detail", args=[self.company.slug]))

        self.assertEqual(response.status_code, HTTP_200_OK)
        serializer = CompanySerializer(
            self.company, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)

    def test_create(self):
        data = {
            "slug": "random-car",
            "owner": "John Doe",
            "name": "Random Car",
            "created_date": "2022-01-01",
            "description": "A random car service company for testing purposes.",
            "phone_number": "+380934567890",
            "email": "info@randomcarservice.com",
            "website": "http://randomcarservice.com",
            "address": "123 Main Street, Cityville",
            "is_verified": True,
        }
        response = self.client.post(reverse("company-list"), data=data, format="json")

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_update(self):
        data = {"description": "Aaaa"}
        response = self.client.patch(
            reverse("company-detail", args=[self.company.slug]),
            data=data,
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.company.refresh_from_db()
        self.assertEqual(self.company.description, "Aaaa")

    def test_delete(self):
        response = self.client.delete(
            reverse("company-detail", args=[self.company.slug])
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


class CarServiceTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="admin", password="124312", email="sad"
        )
        user2 = get_user_model().objects.create_user(username="admi", password="124312")
        self.client.force_authenticate(user)
        self.company = Company.objects.create(
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
            company=self.company,
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

        self.comment = Comment.objects.create(
            user=user, comment_object=self.service, message="hello"
        )

    def test_get(self):
        response = self.client.get(reverse("service-list"))
        serializer = CarServiceSerializer(
            [self.service], many=True, context={"request": response.wsgi_request}
        )

        self.assertEqual(response.data, serializer.data)

    def test_retrieve(self):
        response = self.client.get(reverse("service-detail", args=[self.service.slug]))

        self.assertEqual(response.status_code, HTTP_200_OK)

        rating = self.service.average_rating
        comments = self.service.comment.all()
        comment_serializer = CommentSerializer(
            comments, many=True, context={"request": response.wsgi_request}
        )

        serializer = CarServiceSerializer(
            self.service, context={"request": response.wsgi_request}
        )

        serializer = serializer.data
        serializer["rating"] = rating
        serializer["total_comments"] = comments.count()
        serializer["comments"] = comment_serializer.data

        self.assertEqual(response.data, serializer)

    def test_create(self):
        data = {
            "company": self.company.name,
            "industry": "car wash",
            "slug": "randr",
            "owner": "John Doe",
            "name": "Rando",
            "created_date": "2022-01-01",
            "description": "A random car service",
            "phone_number": "+380934567890",
            "email": "info@randomcarservice.com",
            "address": "123 Main Street, Cityville",
            "is_verified": True,
        }
        response = self.client.post(reverse("service-list"), data=data, format="json")

        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_update(self):
        data = {"description": "ASDA"}
        response = self.client.patch(
            reverse("service-detail", args=[self.service.slug]),
            data=data,
            format="json",
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.service.refresh_from_db()
        self.assertEqual(self.service.description, "ASDA")

    def test_delete(self):
        response = self.client.delete(
            reverse("service-detail", args=[self.service.slug])
        )
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)