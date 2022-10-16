from typing import Any, Dict, List, Optional

import pytest
from django.urls import reverse
from rest_framework import status

from boards.models import Board
from common.utils import reverse_with_query_params
from conftest import APIClientWithUser
from factories import BoardFactory


def boards_url(query_kwargs: Optional[Dict[str, Any]] = None) -> str:
    return reverse_with_query_params("boards:boards", query_kwargs=query_kwargs)


def boards_detail_url(board_id: int) -> str:
    return reverse("boards:board_detail", kwargs={"board_id": board_id})


def boards_join_url(board_id: int) -> str:
    return reverse("boards:board_detail_join", kwargs={"board_id": board_id})


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data",
    [
        {
            "name": "test",
        },
        {
            "name": "TTTTTest",
        },
        {
            "name": "Test_user",
        },
    ],
)
def test_create_board_success(api_client_with_credentials: APIClientWithUser, data: Dict[str, str]) -> None:
    response = api_client_with_credentials.post(boards_url(), data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Board.objects.count() == 1

    board = Board.objects.first()

    assert list(board.members.all()) == [api_client_with_credentials.user]  # type: ignore
    assert list(board.admins.all()) == [api_client_with_credentials.user]  # type: ignore


@pytest.mark.django_db
@pytest.mark.parametrize(
    "data, expected_response_json",
    [
        (
            {
                "name": "a",
            },
            {"name": ["Board name cannot be shorter than 3 characters."]},
        ),
        (
            {
                "name": 21 * "a",
            },
            {"name": ["Board name cannot be longer than 20 characters."]},
        ),
        (
            {
                "name": "test-user",
            },
            {"name": ["Board name can only contain alphabet letters (a-z) and underscore (_) character."]},
        ),
        (
            {
                "name": "test*&user",
            },
            {"name": ["Board name can only contain alphabet letters (a-z) and underscore (_) character."]},
        ),
        (
            {
                "name": "Test_user1",
            },
            {"name": ["Board name can only contain alphabet letters (a-z) and underscore (_) character."]},
        ),
    ],
)
def test_create_board_validation_failed(
    api_client_with_credentials: APIClientWithUser,
    data: Dict[str, str],
    expected_response_json: Dict[str, List[str]],
) -> None:
    response = api_client_with_credentials.post(boards_url(), data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_response_json  # type: ignore[attr-defined]
    assert Board.objects.count() == 0


@pytest.mark.django_db
def test_create_board_name_not_unique(
    api_client_with_credentials: APIClientWithUser,
) -> None:
    BoardFactory(name="Test")

    response = api_client_with_credentials.post(boards_url(), {"name": "Test"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"name": ["Board with this Name already exists."]}  # type: ignore[attr-defined]
    assert Board.objects.count() == 1


@pytest.mark.django_db
def test_get_board_list(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory()
    board_2 = BoardFactory()

    response = api_client_with_credentials.get(boards_url())

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json() == [{"name": board_1.name}, {"name": board_2.name}]


@pytest.mark.django_db
def test_get_board_list_filter_by_name(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory()

    response = api_client_with_credentials.get(boards_url(query_kwargs={"name": board_1.name}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json() == [{"name": board_1.name}]


@pytest.mark.django_db
def test_get_board_list_filter_by_name_multiple_results(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory(name="test 1")
    board_2 = BoardFactory(name="test 2")
    BoardFactory(name="something else")

    response = api_client_with_credentials.get(boards_url(query_kwargs={"name": "test"}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json() == [{"name": board_1.name}, {"name": board_2.name}]


@pytest.mark.django_db
def test_get_board_list_filter_is_member(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory()
    BoardFactory()
    user = api_client_with_credentials.user
    board_1.members.add(user)

    response = api_client_with_credentials.get(boards_url(query_kwargs={"is_member": True}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json() == [{"name": board_1.name}]


@pytest.mark.django_db
def test_get_board_list_filter_is_admin(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory()
    board_2 = BoardFactory()
    BoardFactory()
    user = api_client_with_credentials.user
    board_1.admins.add(user)
    board_2.members.add(user)

    response = api_client_with_credentials.get(boards_url(query_kwargs={"is_admin": True}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json() == [{"name": board_1.name}]


@pytest.mark.django_db
def test_get_board_detail_success(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()

    response = api_client_with_credentials.get(boards_detail_url(board_id=board.pk))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"name": board.name}


@pytest.mark.django_db
def test_get_board_detail_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    response = api_client_with_credentials.get(boards_detail_url(board_id=0))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_join_board(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()
    assert list(board.members.all()) == []

    response = api_client_with_credentials.post(boards_join_url(board_id=board.id))

    assert response.status_code == status.HTTP_200_OK
    assert list(board.members.all()) == [api_client_with_credentials.user]


@pytest.mark.django_db
def test_join_board_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    response = api_client_with_credentials.post(boards_join_url(board_id=0))

    assert response.status_code == status.HTTP_404_NOT_FOUND
