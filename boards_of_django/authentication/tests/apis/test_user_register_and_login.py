from typing import Dict, List, Optional

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from boards_of_django.authentication.models import User
from factories import UserFactory

register_url = reverse("authentication:register")
login_url = reverse("authentication:login")
logout_url = reverse("authentication:logout")


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
@pytest.mark.parametrize(
    "data, expected_status_code, expected_response_json, expected_user_count",
    [
        (
            {
                "email": "test@example.com",
                "username": "test",
                "password": "Str0ng!P@$$w0rd1",
                "password2": "Str0ng!P@$$w0rd2",
            },
            status.HTTP_400_BAD_REQUEST,
            {"password": ["Passwords do not match."]},
            0,
        ),
        (
            {
                "email": "test@example.com",
                "username": "test",
                "password": "test",
                "password2": "test",
            },
            status.HTTP_400_BAD_REQUEST,
            {
                "password": [
                    "This password is too short. It must contain at least 8 characters.",
                    "This password is too common.",
                ]
            },
            0,
        ),
        (
            {
                "username": "test",
                "password": "Str0ng!P@$$w0rd",
                "password2": "Str0ng!P@$$w0rd",
            },
            status.HTTP_400_BAD_REQUEST,
            {"email": ["This field is required."]},
            0,
        ),
        (
            {
                "email": "test@example.com",
                "password": "Str0ng!P@$$w0rd",
                "password2": "Str0ng!P@$$w0rd",
            },
            status.HTTP_400_BAD_REQUEST,
            {"username": ["This field is required."]},
            0,
        ),
        (
            {
                "username": "test",
                "email": "test@example.com",
                "password2": "Str0ng!P@$$w0rd",
            },
            status.HTTP_400_BAD_REQUEST,
            {"password": ["This field is required."]},
            0,
        ),
        (
            {
                "email": "test@example.com",
                "username": "test",
                "password": "Str0ng!P@$$w0rd",
            },
            status.HTTP_400_BAD_REQUEST,
            {"password2": ["This field is required."]},
            0,
        ),
        (
            {
                "email": "test@example.com",
                "username": "t",
                "password": "Str0ng!P@$$w0rd",
                "password2": "Str0ng!P@$$w0rd",
            },
            status.HTTP_400_BAD_REQUEST,
            {"username": ["Username cannot be shorter than 3 characters."]},
            0,
        ),
        (
            {
                "email": "test@example.com",
                "username": 21 * "t",
                "password": "Str0ng!P@$$w0rd",
                "password2": "Str0ng!P@$$w0rd",
            },
            status.HTTP_400_BAD_REQUEST,
            {"username": ["Username cannot be longer than 20 characters."]},
            0,
        ),
    ],
)
def test_register_validation_failed(
    api_client: APIClient,
    data: Dict[str, str],
    expected_status_code: int,
    expected_response_json: Dict[str, List[str]],
    expected_user_count: int,
) -> None:
    assert User.objects.count() == expected_user_count

    response = api_client.post(register_url, data)

    assert response.status_code == expected_status_code
    assert response.json() == expected_response_json
    assert User.objects.count() == expected_user_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "existent_user_data, expected_status_code, expected_response_json, expected_user_count",
    [
        (
            {"email": "test@example.com"},
            status.HTTP_400_BAD_REQUEST,
            {"email": ["User with this Email address already exists."]},
            1,
        ),
        (
            {"username": "test_user"},
            status.HTTP_400_BAD_REQUEST,
            {"username": ["User with this Username already exists."]},
            1,
        ),
    ],
)
def test_register_user_not_unique(
    api_client: APIClient,
    existent_user_data: Dict[str, str],
    expected_status_code: int,
    expected_response_json: Dict[str, List[str]],
    expected_user_count: int,
) -> None:
    UserFactory(**existent_user_data)

    assert User.objects.count() == expected_user_count

    request_data = {
        "email": "test@example.com",
        "username": "test_user",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, request_data)

    assert response.status_code == expected_status_code
    assert response.json() == expected_response_json
    assert User.objects.count() == expected_user_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_data, expected_status_code",
    [
        (
            {"username": "test", "password": "password"},
            status.HTTP_200_OK,
        ),
        (
            {"username": "test", "password": "wrong"},
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_login(
    api_client: APIClient,
    user_data: Dict[str, str],
    expected_status_code: int,
) -> None:
    UserFactory(username="test")

    response = api_client.post(login_url, user_data)

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        assert "token" in response.json()
        assert Token.objects.count() == 1
    else:
        assert response.json() == {"non_field_errors": ["Unable to log in with provided credentials."]}


@pytest.mark.django_db
def test_logout_success(
    api_client: APIClient,
) -> None:
    UserFactory(username="test")

    response_login = api_client.post(login_url, {"username": "test", "password": "password"})

    token = response_login.json()["token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    response = api_client.post(logout_url)

    assert response.status_code == status.HTTP_200_OK
    assert Token.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "token",
    [
        None,
        "wrong",
    ],
)
def test_logout_invalid_token(
    api_client: APIClient,
    token: Optional[str],
) -> None:
    if token is not None:
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    response = api_client.post(logout_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
