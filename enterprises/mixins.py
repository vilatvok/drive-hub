from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from enterprises.permissions import IsOwner


class EnterpriseMixin(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwner]
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
