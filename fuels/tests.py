from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK

from fuels.utils import wog, okko, anp, ukr
from fuels.models import Order, Fuel
from fuels.serializers import (
    FuelSerializer, 
    OrderSerializer, 
    WogSerializer, 
    OkkoSerializer,
    UkrnaftaSerializer,
    AnpSerializer
)
from users.models import Achievement, UserAchievement, Comment, Rating
from users.serializers import CommentSerializer


User = get_user_model()


class FuelTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='admin', password='12345'
        )
        self.client.force_authenticate(user)
        self.fuel = Fuel.objects.create(name='gas', price=51.00)
        self.comment = Comment.objects.create(
            user=user, comment_object=self.fuel, message='hello'
        )
        Rating.objects.create(
            user=user, rate=5, rating_object=self.fuel)
    
    def test_get(self):
        response = self.client.get(reverse('fuel-list'))
        serializer = FuelSerializer(
            [self.fuel], many=True, context={'request': response.wsgi_request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_retrieve(self):
        response = self.client.get(reverse('fuel-detail', args=[self.fuel.slug]))

        rating = self.fuel.average_rating
        comments = self.fuel.comments.all()
        comment_serializer = CommentSerializer(
            comments, many=True, context={'request': response.wsgi_request}
        )

        serializer = FuelSerializer(
            self.fuel, context={'request': response.wsgi_request}
        )
        serializer = serializer.data
        serializer['rating'] = rating
        serializer['total_comments'] = comments.count()
        serializer['comments'] = comment_serializer.data

        self.assertEqual(response.data, serializer)


class OrderTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', password='12345'
        )
        self.client.force_authenticate(self.user)

        self.fuel = Fuel.objects.create(name='gas', price=51.00)
        self.ach = Achievement.objects.create(title='fas', description='sa', bonus=10)
        self.user_ach = UserAchievement.objects.create(user=self.user)
        self.order = Order.objects.create(
            owner=self.user, payment=50, fuel_type=self.fuel, code='123456'
        )

    def test_get(self):
        response = self.client.get(reverse('orders-list'))
        serializer = OrderSerializer([self.order], many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create(self):
        data = {'payment': 540, 'fuel_type': 'gas'}
        response = self.client.post(reverse('orders-list'), data=data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Order.objects.all().count(), 2, Order.objects.all())

    def test_create_with_discount(self):
        self.user_ach.user_achievement.add(self.ach)
        data = {'payment': 540, 'fuel_type': 'gas'}
        response = self.client.post(reverse('orders-list'), data=data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Order.objects.all().count(), 2, Order.objects.all())

    def test_code(self):
        data = {'code': '123456'}
        response = self.client.post(
            reverse('orders-verify-code', args=[self.order.id]),
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, HTTP_200_OK, response.data)
        self.order.refresh_from_db()
        self.assertTrue(self.order.used)


class StationsTest(APITestCase):
    def list_ser(self, url, data, serializer_class):
        response = self.client.get(reverse(url))
        serializer = serializer_class(data[:10], many=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_wog(self):
        url = 'wog_stations'
        self.list_ser(url, wog, WogSerializer)

    def test_okko(self):
        url = 'okko_stations'
        self.list_ser(url, okko, OkkoSerializer)

    def test_ukr(self):
        url = 'ukrnafta_stations'
        self.list_ser(url, ukr, UkrnaftaSerializer)

    def test_anp(self):
        url = 'anp_stations'
        self.list_ser(url, anp, AnpSerializer)
