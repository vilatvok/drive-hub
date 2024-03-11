from datetime import timedelta, datetime, timezone
from decimal import Decimal

from rest_framework import serializers

from fuels.models import Order, Fuel


class FuelSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='fuels-detail', lookup_field='slug'
    )
    coupon = serializers.ReadOnlyField(source='coupon.name')

    class Meta:
        model = Fuel
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    fuel_type = serializers.SlugRelatedField(
        slug_field='name', queryset=Fuel.objects.all()
    )
    code = serializers.CharField(read_only=True)
    used = serializers.BooleanField(read_only=True)
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    # fuel amount
    def get_amount(self, obj):
        ach = obj.owner.achievements.first()
        try:
            date_end = ach.date_achievement + timedelta(days=3)
            if date_end > datetime.now(timezone.utc):
                return Decimal(str(
                    round(obj.payment / (obj.fuel_type.price
                        - (obj.fuel_type.price * ach.user_achievement.get().bonus)
                        / 100), 2)
                    )
                )
        except:
            return Decimal(str(round(obj.payment / obj.fuel_type.price, 2)))


class VerifyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['code']
    

class WogSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    city = serializers.CharField()
    name = serializers.CharField()
    schedule = serializers.DictField()

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        lat = obj['coordinates']['latitude']
        lon = obj['coordinates']['longitude']
        return f'https://www.google.com/maps/place/{lat},{lon}'


class OkkoSerializer(serializers.Serializer):
    city = serializers.CharField(source='Naselenyy_punkt')
    address = serializers.CharField(source='Adresa')
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        lat = obj['coordinates']['lat']
        lon = obj['coordinates']['lng']
        return f'https://www.google.com/maps/place/{lat},{lon}'


class UkrnaftaSerializer(serializers.Serializer):
    address = serializers.CharField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        lat = obj['location']['lat']
        lon = obj['location']['lng']
        return f'https://www.google.com/maps/place/{lat},{lon}'


class AnpSerializer(serializers.Serializer):
    region = serializers.CharField(source='Область')
    district = serializers.CharField(source='Район')
    address = serializers.CharField(source='Адреса')
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        lat = obj['Широта']
        lon = obj['Довгота']
        return f'https://www.google.com/maps/place/{lat},{lon}'


class FuelPricesSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=5, decimal_places=2)
    name = serializers.CharField()
    brand = serializers.CharField(required=False)
    fuel_type = serializers.CharField(required=False)
