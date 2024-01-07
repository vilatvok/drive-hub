from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from phonenumber_field.modelfields import PhoneNumberField

from users.models import Comment, Rating


class Enterprice(models.Model):
    slug = models.SlugField(unique=True, max_length=35)
    name = models.CharField(max_length=50, unique=True)
    owner = models.CharField(max_length=30)
    description = models.TextField()
    email = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField()
    created_date = models.DateField()
    address = models.CharField()
    is_verified = models.BooleanField(default=False)
    added_by = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="%(class)s_added"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Company(Enterprice):
    website = models.URLField(blank=True, null=True)


class CarService(Enterprice):
    INDUSTRY = [("car wash", "Car Wash"), ("car service", "Car Service")]

    industry = models.CharField(choices=INDUSTRY)
    company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="car_service"
    )
    comment = GenericRelation(Comment, related_query_name="service_comment")
    rating = GenericRelation(Rating, related_query_name="service_rating")

    @property
    def average_rating(self):
        rate = self.rating.all()
        count = rate.count()
        if count > 0:
            total = sum(r.rate for r in rate)
            return round(total / count, 2)
        return
