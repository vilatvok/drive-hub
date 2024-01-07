from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED

from django.db.models import Q

from .models import Fine, ElectricCar, FuelCar
from .serializers import *
from .permissions import IsPassport


class CarViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = Pass
    permission_classes = [IsAuthenticated, IsPassport]

    def get_queryset(self):
        elect = ElectricCar.objects.filter(owner=self.request.user).select_related(
            "owner"
        )
        fuel = FuelCar.objects.filter(owner=self.request.user).select_related("owner")
        return (elect, fuel)

    def list(self, request, *args, **kwargs):
        elec, fuel = self.filter_queryset(self.get_queryset())
        fuel_ser = FuelCarSerializer(fuel, many=True)
        elec_ser = ElectricCarSerializer(elec, many=True)
        return Response(fuel_ser.data + elec_ser.data)

    def create(self, request, *args, **kwargs):
        type_car = request.data.get("car_type")

        if type_car == "electric":
            serializer = ElectricCarSerializer(data=request.data)
        elif type_car == "fuel":
            serializer = FuelCarSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)


class FineView(ListAPIView):
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Fine.objects.filter(
                Q(
                    person=self.request.user,
                    fuel__verified="verified",
                )
                | Q(
                    person=self.request.user,
                    elec__verified="verified",
                )
            )
            .select_related("person")
            .prefetch_related("car")
        )
