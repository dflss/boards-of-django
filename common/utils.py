from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


def raise_django_exception_as_drf_exception(exc: Exception, ctx: Dict[str, Any]) -> Optional[Response]:
    """Create custom exception handler.

    Map between django.core.exceptions.ValidationError and
    rest_framework.exceptions.ValidationError.

    Explained in https://github.com/HackSoftware/Django-Styleguide#djangos-validationerror.
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    response = exception_handler(exc, ctx)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response

    return response
