from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from fuel_store.models import Fuel


# Create your models here.
class Car(models.Model):
    VERIFY_CHOICES = [
        ("pending", "Pending Verification"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="%(class)s_owner"
    )
    name = models.CharField(max_length=50)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(2023)]
    )
    image = models.ImageField(upload_to="car/", blank=True)

    registration_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[MinLengthValidator(8), MaxLengthValidator(8)],
    )
    verified = models.CharField(
        max_length=20, choices=VERIFY_CHOICES, default="pending"
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class FuelCar(Car):
    fuel_efficiency = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    fuel_type = models.ForeignKey(Fuel, on_delete=models.SET, related_name="car")
    fuel_relation = GenericRelation("Fine", related_query_name="fuel")


class ElectricCar(Car):
    battery = models.PositiveIntegerField()
    power_reserve = models.PositiveIntegerField()
    electric_relation = GenericRelation("Fine", related_query_name="elec")


class Fine(models.Model):
    FINES = [("speed", "Limit speed"), ("state", "Alcohol")]
    person = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="fine"
    )
    type_of_fine = models.CharField(max_length=40, choices=FINES)
    sum_of_fine = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("fuelcar", "electriccar")},
    )
    object_id = models.PositiveIntegerField()
    car = GenericForeignKey("content_type", "object_id")

    def save(self, *args, **kwargs):
        if self.car:
            return super().save(*args, **kwargs)

    def __str__(self):
        return self.type_of_fine
