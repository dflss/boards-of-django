from collections import OrderedDict
from typing import Any, List, Type

from django.db.models import QuerySet
from rest_framework.pagination import BasePagination
from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView


def get_paginated_response(
    *,
    pagination_class: Type[BasePagination],
    serializer_class: Type[Serializer[Any]],
    queryset: QuerySet[Any],
    request: Request,
    view: APIView
) -> Response:
    """
    Return a paginated response.

    This code is taken from Django-Styleguide: https://github.com/HackSoftware/Django-Styleguide#filters--pagination
    """
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(data=serializer.data)


class LimitOffsetPagination(_LimitOffsetPagination):
    """
    Base class for Pagination classes used in APIs.

    This code is taken from Django-Styleguide: https://github.com/HackSoftware/Django-Styleguide#filters--pagination
    """

    default_limit = 10
    max_limit = 50

    def get_paginated_response(self, data: List[Any]) -> Response:
        """
        Return paginated response.

        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
