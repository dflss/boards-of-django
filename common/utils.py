from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from django.utils.http import urlencode
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


def reverse_with_query_params(
    viewname: str, kwargs: Optional[Dict[Any, Any]] = None, query_kwargs: Optional[Dict[str, Any]] = None
) -> str:
    """Reverse a url that contains query parameters.

    This function can be used for example with search filters, as Django's reverse does not support query parameters
    at the moment.

    Example usage:
        reverse_with_query_params('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})

    Parameters
    ----------
    viewname : Name of the view
    kwargs : Dictionary where key is the name of the ulr param and value is its value
    query_kwargs : Dictionary where key is the name of the query param and value is its value

    Returns
    -------
    Url string
    """
    base_url = reverse(viewname, kwargs=kwargs)
    if query_kwargs:
        return f"{base_url}?{urlencode(query_kwargs)}"
    return base_url
