from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StationPaginate(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class BaseStationMixin(ListAPIView):
    """Mixin for apiview stations."""

    pagination_class = StationPaginate
    serializer_class = None
    queryset = None
    city_field = None

    def get_queryset(self):
        return self.queryset

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        city = request.query_params.get('city')
        if city:
            filter_query = [
                station
                for station in queryset
                if city.title() in station[self.city_field]
            ]
        else:
            filter_query = queryset

        page = self.paginate_queryset(filter_query)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
