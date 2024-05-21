from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)

from fuels.models import Fuel


User = get_user_model()


def validate_number(value):
    elec_not_unique = ElectricCar.objects.filter(registration_number=value)
    fuel_not_unique = FuelCar.objects.filter(registration_number=value)
    if elec_not_unique or fuel_not_unique:
        raise ValidationError('Registration number must be unique')


# Create your models here.
class Car(models.Model):
    VERIFY_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='%(class)s_owner',
    )
    name = models.CharField(max_length=50)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(2023)]
    )
    registration_number = models.CharField(
        max_length=20,
        validators=[
            MinLengthValidator(8),
            MaxLengthValidator(8),
            validate_number,
        ],
    )
    image = models.ImageField(upload_to='cars/')
    verified = models.CharField(
        max_length=20,
        choices=VERIFY_CHOICES,
        default='pending',
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class FuelCar(Car):
    fuel_efficiency = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)],
    )
    fuel_type = models.ForeignKey(
        to=Fuel,
        on_delete=models.SET,
        related_name='car',
    )
    fuel_relation = GenericRelation(to='Fine', related_query_name='fuel')


class ElectricCar(Car):
    battery = models.PositiveIntegerField()
    power_reserve = models.PositiveIntegerField()
    electric_relation = GenericRelation('Fine', related_query_name='elec')


class Fine(models.Model):
    FINES = [('speed', 'Limit speed'), ('state', 'Alcohol')]
    person = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='fine',
    )
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={'model__in': ('fuelcar', 'electriccar')},
    )
    object_id = models.PositiveIntegerField()
    car = GenericForeignKey('content_type', 'object_id')
    type_of_fine = models.CharField(max_length=40, choices=FINES)
    sum_of_fine = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.car:
            return super().save(*args, **kwargs)

    def __str__(self):
        return self.type_of_fine
