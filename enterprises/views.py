from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from django.contrib.contenttypes.models import ContentType

from users.models import Rating

from .models import Company, CarService
from .serializers import CompanySerializer, CarServiceSerializer
from .mixins import EnterpriseMixin

from users.serializers import CommentSerializer, RatingSerializer


class CompanyViewSet(EnterpriseMixin):
    queryset = Company.objects.all().select_related("added_by")
    serializer_class = CompanySerializer


class CarServiceViewSet(EnterpriseMixin):
    queryset = CarService.objects.all().select_related("added_by")
    serializer_class = CarServiceSerializer

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
        service = self.get_object()
        content = ContentType.objects.get_for_model(CarService)

        r = Rating.objects.filter(
            user=request.user, content_type=content, object_id=service.id
        )
        if not r.exists():
            serializer = RatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=request.user, content_type=content, object_id=service.id
            )
            return Response(serializer.data, status=HTTP_201_CREATED)
        else:
            serializer = RatingSerializer(r.first(), data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # add comment function
    @action(detail=True, methods=["post"])
    def comment(self, request, slug=None):
        service = self.get_object()
        content_type = ContentType.objects.get_for_model(CarService)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user, content_type=content_type, object_id=service.id
        )
        return Response(serializer.data, status=HTTP_201_CREATED)
