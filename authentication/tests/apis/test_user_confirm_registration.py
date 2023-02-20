import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from factories import ConfirmationTokenFactory, UserFactory

confirm_registration_url = reverse("authentication:confirm-registration")


@pytest.mark.django_db
def test_confirm_registration_success(api_client: APIClient) -> None:
    user = UserFactory(is_active=False)
    confirmation_token = ConfirmationTokenFactory(user=user)

    data = {"token": confirmation_token.token}

    response = api_client.post(confirm_registration_url, data)

    user.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert user.is_active


@pytest.mark.django_db
def test_confirm_registration_invalid_token(api_client: APIClient) -> None:
    user = UserFactory(is_active=False)

    data = {"token": "wrong_token"}

    response = api_client.post(confirm_registration_url, data)

    user.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"token": ["Token is invalid."]}
    assert not user.is_active
