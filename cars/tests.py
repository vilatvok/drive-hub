from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED

from .models import FuelCar, ElectricCar, Fine
from .serializers import FuelCarSerializer, ElectricCarSerializer, FineSerializer

from fuel_store.models import Fuel
from users.models import Passport

from datetime import datetime, timedelta, timezone


class CarTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="admin", password="12345")

        self.client.force_authenticate(user)
        current_time = datetime.now(timezone.utc)
        passport = Passport.objects.create(
            user=user,
            id_number="123456789",
            tax_number="1234567890",
            date_issue=current_time - timedelta(days=365),
            date_expiry=current_time,
        )

        self.fuel = Fuel.objects.create(name="gas", price=51.00)

        self.fuel_car = FuelCar.objects.create(
            owner=user,
            name="sdad",
            year=2012,
            image="sda",
            registration_number="12345678",
            fuel_efficiency=25,
            fuel_type=self.fuel,
        )

        self.elec_car = ElectricCar.objects.create(
            owner=user,
            name="sd",
            year=2018,
            image="s",
            registration_number="12345674",
            battery=678,
            power_reserve=679,
        )

    def test_get(self):
        response = self.client.get(reverse("cars-list"))
        serializer = FuelCarSerializer([self.fuel_car], many=True)
        serializer_ = ElectricCarSerializer([self.elec_car], many=True)
        self.assertEqual(
            response.data, serializer.data + serializer_.data, response.content
        )

    def test_create(self):
        data = {
            "car_type": "fuel",
            "name": "asd",
            "year": 1998,
            "registration_number": "12345676",
            "fuel_efficiency": 25,
            "fuel_type": self.fuel.name,
        }

        data_ = {
            "car_type": "electric",
            "name": "asdvb",
            "year": 2005,
            "registration_number": "12345689",
            "battery": 25,
            "power_reserve": 67,
        }

        response = self.client.post(reverse("cars-list"), data=data, format="json")
        response_ = self.client.post(reverse("cars-list"), data=data_, format="json")
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response_.status_code, HTTP_201_CREATED)


class FineTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="admin", password="12345")
        self.client.force_authenticate(user)

        current_time = datetime.now(timezone.utc)
        Passport.objects.create(
            user=user,
            id_number="123456789",
            tax_number="1234567890",
            date_issue=current_time - timedelta(days=365),
            date_expiry=current_time,
        )

        fuel = Fuel.objects.create(name="gas", price=51.00)

        fuel_car = FuelCar.objects.create(
            owner=user,
            name="sdad",
            year=2012,
            image="sda",
            registration_number="12345678",
            fuel_efficiency=25,
            fuel_type=fuel,
            verified="verified",
        )
        self.fine = Fine.objects.create(
            person=user,
            type_of_fine="speed",
            sum_of_fine=400,
            car=fuel_car,
        )

    def test_get(self):
        response = self.client.get(reverse("fines"))
        serializer = FineSerializer([self.fine], many=True)
        self.assertEqual(response.data, serializer.data)
