from typing import Any, Generator

import pytest
from django.contrib.auth.models import AnonymousUser
from pytest_factoryboy import register
from rest_framework.test import APIClient

from authentication.models import User
from factories import UserFactory

register(UserFactory)


class APIClientWithUser(APIClient):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.user: User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def api_client_with_credentials() -> Generator[APIClientWithUser, None, None]:
    api_client = APIClientWithUser()
    user = UserFactory.create()
    api_client.user = user
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=AnonymousUser())
