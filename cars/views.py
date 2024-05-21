from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from cars.models import Fine, ElectricCar, FuelCar
from cars.serializers import (
    FuelCarSerializer,
    ElectricCarSerializer,
    FineSerializer,
)
from cars.permissions import IsPassport


class CarViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsPassport]
    lookup_field = 'registration_number'

    def get_queryset(self):
        elect = (
            ElectricCar.objects.select_related('owner').
            filter(owner=self.request.user)
        )
        fuel = (
            FuelCar.objects.select_related('owner').
            filter(owner=self.request.user)
        )
        return (elect, fuel)

    def list(self, request, *args, **kwargs):
        elec, fuel = self.get_queryset()
        fuel_serializer = FuelCarSerializer(instance=fuel, many=True)
        elec_serializer = ElectricCarSerializer(instance=elec, many=True)
        return Response(fuel_serializer.data + elec_serializer.data)

    def create(self, request, *args, **kwargs):
        type_car = request.data.get('car_type')

        if type_car == 'electric':
            serializer = ElectricCarSerializer(data=request.data)
        elif type_car == 'fuel':
            serializer = FuelCarSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get_object(self):
        q, q2 = self.get_queryset()

        lookup_url_kwarg = self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {lookup_url_kwarg: self.kwargs[lookup_url_kwarg]}
        try:
            obj = get_object_or_404(q, **filter_kwargs)
        except Http404:
            obj = get_object_or_404(q2, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'fuel_efficiency'):
            serializer = FuelCarSerializer(instance)
        else:
            serializer = ElectricCarSerializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FineViewSet(ReadOnlyModelViewSet):
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Fine.objects.select_related('person').prefetch_related('car').
            filter(
                Q(person=user, fuel__verified='verified') |
                Q(person=user, elec__verified='verified'),
            )
        )
