from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_201_CREATED
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsOwner


class EnterpriseMixin(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwner]
    lookup_field = "slug"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(added_by=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)
    
