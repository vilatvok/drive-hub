import random

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from django.contrib.contenttypes.models import ContentType

from .utils import *
from .serializers import *
from .models import Order, Fuel
from .mixins import BaseStationMixin

from users.models import Comment, Rating
from users.serializers import CommentSerializer, RatingSerializer


class FuelViewSet(ReadOnlyModelViewSet):
    queryset = Fuel.objects.all()
    serializer_class = FuelSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        resp = self.get_serializer(obj)

        rating = obj.average_rating
        comments = obj.comment.select_related("user").prefetch_related("likes")
        com_serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )

        response = resp.data
        response["rating"] = rating
        response["total_comments"] = comments.count()
        response["comments"] = com_serializer.data

        return Response(response)

    # rate the object
    @action(detail=True, methods=["post"])
    def rate(self, request, slug=None):
        fuel = self.get_object()
        content = ContentType.objects.get_for_model(Fuel)

        r = Rating.objects.filter(
            user=request.user, content_type=content, object_id=fuel.id
        )
        if not r.exists():
            serializer = RatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=request.user, content_type=content, object_id=fuel.id
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            serializer = RatingSerializer(r.first(), data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # add comment
    @action(detail=True, methods=["post"])
    def comment(self, request, slug=None):
        fuel = self.get_object()
        content_type = ContentType.objects.get_for_model(Fuel)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, content_type=content_type, object_id=fuel.id)
        return Response(serializer.data, status=HTTP_201_CREATED)


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user).select_related(
            "owner", "fuel_type"
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = str(random.randint(100000, 999999))
        serializer.save(owner=request.user, code=code)

        # save temporary code in session
        id = str(serializer.instance.id)
        request.session[id] = code

        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def verify_code(self, request, pk=None):
        order = self.get_object()
        # if order hasnt been used yet then activate order and delete
        # code from session
        if order.used == False:
            order.used = True
            order.save()
            del request.session[str(order.id)]
            return Response({"status": "success"})
        return Response({"status": "error"}, status=HTTP_400_BAD_REQUEST)


class FuelPricesView(ListAPIView):
    serializer_class = FuelPricesSerializer

    def get_queryset(self):
        return prices

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        okko = queryset["okko"]
        wog = queryset["wog"]
        ukrnafta = queryset["ukrnafta"]
        anp = queryset["anp"]

        okko_serializer = self.get_serializer(okko, many=True)
        wog_serializer = self.get_serializer(wog, many=True)
        ukrnafta_serializer = self.get_serializer(ukrnafta, many=True)
        anp_serializer = self.get_serializer(anp, many=True)

        data = {
            "okko": okko_serializer.data,
            "wog": wog_serializer.data,
            "ukrnafta": ukrnafta_serializer.data,
            "anp": anp_serializer.data,
        }
        return Response(data)


class CommentLike(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, *args, **kwargs):
        comment = Comment.objects.get(id=comment_id)
        if comment.likes.filter(id=request.user.id).exists():
            comment.likes.remove(request.user)
            comment.save()
            return Response({"status": "error"}, status=HTTP_400_BAD_REQUEST)
        else:
            comment.likes.add(request.user)
            comment.save()
            return Response({"status": "success"})


class WogViewSet(BaseStationMixin):
    serializer_class = WogSerializer
    queryset = wog
    city_field = "city"


class OkkoViewSet(BaseStationMixin):
    serializer_class = OkkoSerializer
    queryset = okko
    city_field = "Naselenyy_punkt"


class UkrnaftaViewSet(BaseStationMixin):
    serializer_class = UkrnaftaSerializer
    queryset = ukr
    city_field = "address"


class AnpViewSet(BaseStationMixin):
    serializer_class = AnpSerializer
    queryset = anp
    city_field = "Район"
