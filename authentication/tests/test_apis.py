import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from factories import UserFactory

register_url = reverse("authentication:auth:register")


@pytest.mark.django_db
def test_register_success(api_client: APIClient) -> None:
    assert User.objects.count() == 0

    data = {
        "email": "test@example.com",
        "username": "test",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_register_passwords_not_matching(api_client: APIClient) -> None:
    assert User.objects.count() == 0

    data = {
        "email": "test@example.com",
        "username": "test",
        "password": "Str0ng!P@$$w0rd1",
        "password2": "Str0ng!P@$$w0rd2",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # mypy ignored because of https://github.com/typeddjango/djangorestframework-stubs/issues/230
    assert response.json() == {"password": ["Passwords do not match."]}  # type: ignore[attr-defined]
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_register_passwords_validation(api_client: APIClient) -> None:
    assert User.objects.count() == 0

    data = {
        "email": "test@example.com",
        "username": "test",
        "password": "test",
        "password2": "test",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {  # type: ignore[attr-defined]
        "password": [
            "This password is too short. It must contain at least 8 characters.",
            "This password is too common.",
        ]
    }
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_register_email_missing(api_client: APIClient) -> None:
    assert User.objects.count() == 0

    data = {
        "username": "test",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"email": ["This field is required."]}  # type: ignore[attr-defined]
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_register_username_missing(api_client: APIClient) -> None:
    assert User.objects.count() == 0

    data = {
        "email": "test@example.com",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"username": ["This field is required."]}  # type: ignore[attr-defined]
    assert User.objects.count() == 0


@pytest.mark.django_db
def test_register_email_not_unique(api_client: APIClient) -> None:
    UserFactory(email="test@example.com")
    assert User.objects.count() == 1

    data = {
        "email": "test@example.com",
        "username": "test",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"email": ["User with this Email address already exists."]}  # type: ignore[attr-defined]
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_register_username_not_unique(api_client: APIClient) -> None:
    UserFactory(username="test_user")
    assert User.objects.count() == 1

    data = {
        "email": "test@example.com",
        "username": "test_user",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"username": ["User with this Username already exists."]}  # type: ignore[attr-defined]
    assert User.objects.count() == 1
