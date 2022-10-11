from typing import Annotated, Dict, List

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


_invalid_user_input_data = [
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
]


@pytest.mark.django_db
@pytest.mark.parametrize("data, expected_status_code, response_json, user_count", _invalid_user_input_data)
def test_register_validation_failed(
    api_client: APIClient,
    data: Annotated[Dict[str, str], pytest.fixture],
    expected_status_code: Annotated[int, pytest.fixture],
    response_json: Annotated[Dict[str, List[str]], pytest.fixture],
    user_count: Annotated[int, pytest.fixture],
) -> None:
    assert User.objects.count() == user_count

    response = api_client.post(register_url, data)

    assert response.status_code == expected_status_code
    # mypy ignored because of https://github.com/typeddjango/djangorestframework-stubs/issues/230
    assert response.json() == response_json  # type: ignore[attr-defined]
    assert User.objects.count() == user_count


_existent_user_input_data = [
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
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "existent_user_data, expected_status_code, response_json, user_count", _existent_user_input_data
)
def test_register_user_not_unique(
    api_client: APIClient,
    existent_user_data: Annotated[Dict[str, str], pytest.fixture],
    expected_status_code: Annotated[int, pytest.fixture],
    response_json: Annotated[Dict[str, List[str]], pytest.fixture],
    user_count: Annotated[int, pytest.fixture],
) -> None:
    UserFactory(**existent_user_data)

    assert User.objects.count() == user_count

    request_data = {
        "email": "test@example.com",
        "username": "test_user",
        "password": "Str0ng!P@$$w0rd",
        "password2": "Str0ng!P@$$w0rd",
    }

    response = api_client.post(register_url, request_data)

    assert response.status_code == expected_status_code
    assert response.json() == response_json  # type: ignore[attr-defined]
    assert User.objects.count() == user_count