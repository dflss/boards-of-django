import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from factories import ConfirmationOTPFactory, UserFactory

confirm_registration_url = reverse("authentication:confirm-registration")


@pytest.mark.django_db
def test_confirm_registration_success(api_client: APIClient) -> None:
    user = UserFactory(is_active=False)
    confirmation_otp = ConfirmationOTPFactory(user=user)
    data = {"email": user.email, "otp": confirmation_otp.otp}

    response = api_client.post(confirm_registration_url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_confirm_registration_invalid_email(api_client: APIClient) -> None:
    data = {"email": "wrong@example.com", "otp": "wrong_otp"}

    response = api_client.post(confirm_registration_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"email": ["Email is invalid."]}


@pytest.mark.django_db
def test_confirm_registration_invalid_otp(api_client: APIClient) -> None:
    user = UserFactory(is_active=False)
    data = {"email": user.email, "otp": "wrong_otp"}

    response = api_client.post(confirm_registration_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"otp": ["One-time password is invalid."]}
