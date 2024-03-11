from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation

from fuels.tasks import get_price, get_default_price, coupon_scheduler

from users.tasks import get_orders_achievement
from users.models import Comment, Rating


class Fuel(models.Model):
    slug = models.SlugField(unique=True, max_length=30)
    name = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fuel',
    )
    date_update = models.DateTimeField(auto_now=True)
    comments = GenericRelation(Comment, related_query_name='fuel_comment')
    rating = GenericRelation(Rating, related_query_name='fuel_rating')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__coupon = self.coupon
        self.__discount = self.coupon

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        rate = self.rating.all()
        count = rate.count()
        if count > 0:
            total = sum(r.rate for r in rate)
            return round(total / count, 2)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # when coupon started
        if self.coupon != self.__coupon and self.coupon is not None:
            get_price.delay(self.id)
            self.__coupon = self.coupon
        # when coupon expired
        elif self.coupon != self.__coupon and self.coupon is None:
            get_default_price.delay(self.id, self.__discount.discount)
            self.__coupon = self.coupon
        return super().save(*args, **kwargs)


class Order(models.Model):
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='orders'
    )
    fuel_type = models.ForeignKey(
        'Fuel', on_delete=models.CASCADE, related_name='order'
    )
    payment = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    code = models.CharField(validators=[MinLengthValidator(6)], max_length=6)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.fuel_type.name} - {self.payment} - {self.amount}'

    def save(self, *args, **kwargs):
        # assign achievement to user
        if self.owner.orders.all().count() == 50:
            get_orders_achievement.delay(self.owner.id)
        return super().save(*args, **kwargs)


class Coupon(models.Model):
    name = models.CharField(max_length=30, unique=True)
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    state = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.discount}%'

    def save(self, *args, **kwargs):
        coupon_scheduler(self.id, self.date_start, self.date_end)
        return super().save(*args, **kwargs)
