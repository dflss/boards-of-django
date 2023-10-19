from typing import TYPE_CHECKING, Any

import pytest
from django.contrib.auth.models import AnonymousUser
from pytest_factoryboy import register
from rest_framework.test import APIClient

from factories import UserFactory

if TYPE_CHECKING:
    from collections.abc import Generator

    from boards_of_django.authentication.models import User

register(UserFactory)


class APIClientWithUser(APIClient):
    """API client that automatically authenticates user."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """API client that automatically authenticates user."""
        super().__init__(*args, **kwargs)
        self.user: "User"


@pytest.fixture()
def api_client() -> APIClient:
    """API client fixture."""
    return APIClient()


@pytest.fixture()
@pytest.mark.django_db()
def api_client_with_credentials() -> "Generator[APIClientWithUser, None, None]":
    """API client fixture that automatically authenticates user."""
    api_client = APIClientWithUser()
    user = UserFactory.create()
    api_client.user = user
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=AnonymousUser())
