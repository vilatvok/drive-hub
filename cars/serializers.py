from rest_framework import serializers

from .models import Fine, ElectricCar, FuelCar

from fuel_store.models import Fuel


class Pass(serializers.Serializer):
    pass


class CarRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, ElectricCar):
            return value.name
        elif isinstance(value, FuelCar):
            return value.name
        raise "Unexpected car type"


class ElectricCarSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    verified = serializers.ReadOnlyField()

    class Meta:
        model = ElectricCar
        fields = "__all__"


class FuelCarSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    fuel_type = serializers.SlugRelatedField(
        slug_field="name", queryset=Fuel.objects.all()
    )
    verified = serializers.ReadOnlyField()

    class Meta:
        model = FuelCar
        fields = "__all__"


class FineSerializer(serializers.ModelSerializer):
    car = CarRelatedField(read_only=True)

    class Meta:
        model = Fine
        exclude = ["person", "object_id", "content_type"]
