import random

from django.contrib.contenttypes.models import ContentType

from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from fuels import serializers
from fuels.utils import okko, wog, ukr, anp, prices
from fuels.models import Order, Fuel
from fuels.mixins import BaseStationMixin

from users.models import Rating
from users.serializers import CommentSerializer, RatingSerializer


class FuelViewSet(ReadOnlyModelViewSet):
    queryset = Fuel.objects.all()
    serializer_class = serializers.FuelSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        resp = self.get_serializer(obj)

        rating = obj.average_rating
        comments = obj.comments.select_related('user').prefetch_related('likes')
        com_serializer = CommentSerializer(
            instance=comments,
            many=True,
            context={'request': request},
        )

        response = resp.data
        response['rating'] = rating
        response['total_comments'] = comments.count()
        response['comments'] = com_serializer.data

        return Response(response)

    @action(detail=True, methods=['post'])
    def rate(self, request, slug=None):
        fuel = self.get_object()
        content = ContentType.objects.get_for_model(Fuel)

        rating = Rating.objects.filter(
            user=request.user,
            content_type=content,
            object_id=fuel.id,
        )
        if not rating.exists():
            serializer = RatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=request.user,
                content_type=content,
                object_id=fuel.id,
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            serializer = RatingSerializer(
                instance=rating.first(),
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-comment')
    def add_comment(self, request, slug=None):
        fuel = self.get_object()
        content_type = ContentType.objects.get_for_model(Fuel)
        serializer = CommentSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            content_type=content_type,
            object_id=fuel.id,
        )
        return Response(serializer.data, status.HTTP_201_CREATED)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user).select_related(
            'owner',
            'fuel_type',
        )

    def perform_create(self, serializer):
        code = str(random.randint(100000, 999999))
        serializer.save(owner=self.request.user, code=code)

    @action(detail=True, methods=['post'], url_path='verify-code')
    def verify_code(self, request, pk=None):
        """
        If order hasnt been used yet, then activate order and
        delete code from session.
        """
        order = self.get_object()
        serializer = serializers.VerifyOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if order.used:
            return Response(
                data={'status': 'This code has been already used'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif serializer.validated_data['code'] != order.code:
            return Response(
                data={'status': 'Wrong code'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.used = True
        order.save()
        return Response({'status': 'success'})


class FuelPricesAPIView(ListAPIView):
    serializer_class = serializers.FuelPricesSerializer

    def get_queryset(self):
        return prices

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        okko = queryset['okko']
        wog = queryset['wog']
        ukrnafta = queryset['ukrnafta']
        anp = queryset['anp']

        okko_serializer = self.get_serializer(okko, many=True)
        wog_serializer = self.get_serializer(wog, many=True)
        ukrnafta_serializer = self.get_serializer(ukrnafta, many=True)
        anp_serializer = self.get_serializer(anp, many=True)

        data = {
            'okko': okko_serializer.data,
            'wog': wog_serializer.data,
            'ukrnafta': ukrnafta_serializer.data,
            'anp': anp_serializer.data,
        }
        return Response(data)


class WogAPIView(BaseStationMixin):
    serializer_class = serializers.WogSerializer
    queryset = wog
    city_field = 'city'


class OkkoAPIView(BaseStationMixin):
    serializer_class = serializers.OkkoSerializer
    queryset = okko
    city_field = 'Naselenyy_punkt'


class UkrnaftaAPIView(BaseStationMixin):
    serializer_class = serializers.UkrnaftaSerializer
    queryset = ukr
    city_field = 'address'


class AnpAPIView(BaseStationMixin):
    serializer_class = serializers.AnpSerializer
    queryset = anp
    city_field = 'Район'
