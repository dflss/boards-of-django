from typing import Any, Dict, List, Optional

import pytest
from django.urls import reverse
from rest_framework import status

from boards.models import Board, Comment, Post
from common.utils import reverse_with_query_params
from conftest import APIClientWithUser
from factories import BoardFactory, CommentFactory, PostFactory, UserFactory


def boards_url(query_kwargs: Optional[Dict[str, Any]] = None) -> str:
    return reverse_with_query_params("boards:boards", query_kwargs=query_kwargs)


def boards_detail_url(board_id: int) -> str:
    return reverse("boards:board-detail", kwargs={"board_id": board_id})


def boards_join_url(board_id: int) -> str:
    return reverse("boards:board-detail-join", kwargs={"board_id": board_id})


def boards_add_admin_url(board_id: int) -> str:
    return reverse("boards:board-detail-add-admin", kwargs={"board_id": board_id})


def posts_url(query_kwargs: Optional[Dict[str, Any]] = None) -> str:
    return reverse_with_query_params("boards:posts", query_kwargs=query_kwargs)


def posts_detail_url(post_id: int) -> str:
    return reverse("boards:post-detail", kwargs={"post_id": post_id})


def comments_url(query_kwargs: Optional[Dict[str, Any]] = None) -> str:
    return reverse_with_query_params("boards:comments", query_kwargs=query_kwargs)


def comments_detail_url(comment_id: int) -> str:
    return reverse("boards:comment-detail", kwargs={"comment_id": comment_id})


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
            {"name": ["Ensure this value has at least 3 characters (it has 1)."]},
        ),
        (
            {
                "name": 21 * "a",
            },
            {"name": ["Ensure this value has at most 20 characters (it has 21)."]},
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
    assert len(response.json()["results"]) == 2
    assert response.json()["results"] == [{"name": board_1.name}, {"name": board_2.name}]


@pytest.mark.django_db
def test_get_board_list_filter_by_name(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory()

    response = api_client_with_credentials.get(boards_url(query_kwargs={"name": board_1.name}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [{"name": board_1.name}]


@pytest.mark.django_db
def test_get_board_list_filter_by_name_multiple_results(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory(name="test 1")
    board_2 = BoardFactory(name="test 2")
    BoardFactory(name="something else")

    response = api_client_with_credentials.get(boards_url(query_kwargs={"name": "test"}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2
    assert response.json()["results"] == [{"name": board_1.name}, {"name": board_2.name}]


@pytest.mark.django_db
def test_get_board_list_filter_is_member(api_client_with_credentials: APIClientWithUser) -> None:
    board_1 = BoardFactory()
    BoardFactory()
    user = api_client_with_credentials.user
    board_1.members.add(user)

    response = api_client_with_credentials.get(boards_url(query_kwargs={"is_member": True}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [{"name": board_1.name}]


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
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [{"name": board_1.name}]


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


@pytest.mark.django_db
def test_add_admin_to_board(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()
    board.admins.add(api_client_with_credentials.user)
    user_to_add = UserFactory()
    board.members.add(user_to_add)

    response = api_client_with_credentials.post(
        boards_add_admin_url(board_id=board.id), data={"users_to_add": [user_to_add.id]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert list(board.admins.all()) == [api_client_with_credentials.user, user_to_add]


@pytest.mark.django_db
def test_add_admin_who_is_already_an_admin_to_board(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()
    board.admins.add(api_client_with_credentials.user)
    user_to_add = UserFactory()
    board.members.add(user_to_add)
    board.admins.add(user_to_add)

    response = api_client_with_credentials.post(
        boards_add_admin_url(board_id=board.id), data={"users_to_add": [user_to_add.id]}
    )

    assert response.status_code == status.HTTP_200_OK
    assert list(board.admins.all()) == [api_client_with_credentials.user, user_to_add]


@pytest.mark.django_db
def test_add_admin_who_is_not_a_member_to_board(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()
    board.admins.add(api_client_with_credentials.user)
    user_to_add = UserFactory()

    response = api_client_with_credentials.post(
        boards_add_admin_url(board_id=board.id), data={"users_to_add": [user_to_add.id]}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"users_to_add": ["Only board members can be added as board admins."]}  # type: ignore


@pytest.mark.django_db
def test_add_admin_by_user_that_is_not_an_admin(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()
    user_to_add = UserFactory()

    response = api_client_with_credentials.post(
        boards_add_admin_url(board_id=board.id), data={"users_to_add": [user_to_add.id]}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Only board admin can perform this action."}  # type: ignore


@pytest.mark.django_db
def test_add_admin_board_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    user_to_add = UserFactory()

    response = api_client_with_credentials.post(
        boards_add_admin_url(board_id=0), data={"users_to_add": [user_to_add.id]}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_post_success(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()
    board.members.add(api_client_with_credentials.user)

    response = api_client_with_credentials.post(posts_url(), {"text": "test test test", "board": board.id})

    assert response.status_code == status.HTTP_201_CREATED
    assert Post.objects.count() == 1

    post = Post.objects.first()

    assert post.creator == api_client_with_credentials.user  # type: ignore
    assert post.board == board  # type: ignore


@pytest.mark.django_db
@pytest.mark.parametrize(
    "text, expected_response_json",
    [
        (
            "test",
            {"text": ["Ensure this value has at least 10 characters (it has 4)."]},
        ),
        (
            1001 * "a",
            {"text": ["Ensure this value has at most 1000 characters (it has 1001)."]},
        ),
    ],
)
def test_create_post_validation_failed(
    api_client_with_credentials: APIClientWithUser,
    text: str,
    expected_response_json: Dict[str, List[str]],
) -> None:
    board = BoardFactory()
    board.members.add(api_client_with_credentials.user)

    response = api_client_with_credentials.post(posts_url(), {"text": text, "board": board.id})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_response_json  # type: ignore[attr-defined]
    assert Post.objects.count() == 0


@pytest.mark.django_db
def test_cannot_create_post_if_not_a_board_member(api_client_with_credentials: APIClientWithUser) -> None:
    board = BoardFactory()

    response = api_client_with_credentials.post(posts_url(), {"text": "test test test", "board": board.id})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {  # type: ignore
        "board": ["Only board members can add posts. You are not a member of this board."]
    }


@pytest.mark.django_db
def test_get_post_list(api_client_with_credentials: APIClientWithUser) -> None:
    post_1 = PostFactory()
    post_2 = PostFactory()

    response = api_client_with_credentials.get(posts_url())

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2
    assert response.json()["results"] == [
        {"text": post_2.text, "creator": {"id": post_2.creator.id, "username": post_2.creator.username}},
        {"text": post_1.text, "creator": {"id": post_1.creator.id, "username": post_1.creator.username}},
    ]


@pytest.mark.django_db
def test_get_post_list_filter_by_text(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory(text="Text that I am looking for")
    PostFactory(text="Something unimportant")

    response = api_client_with_credentials.get(posts_url(query_kwargs={"text": "I am looking"}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {"text": post.text, "creator": {"id": post.creator.id, "username": post.creator.username}},
    ]


@pytest.mark.django_db
def test_get_post_list_filter_by_board(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory()
    PostFactory()

    response = api_client_with_credentials.get(posts_url(query_kwargs={"board": post.board.id}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {"text": post.text, "creator": {"id": post.creator.id, "username": post.creator.username}},
    ]


@pytest.mark.django_db
def test_get_post_list_filter_own_posts(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory(creator=api_client_with_credentials.user)
    PostFactory(creator=UserFactory())

    response = api_client_with_credentials.get(posts_url(query_kwargs={"is_creator": True}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {"text": post.text, "creator": {"id": post.creator.id, "username": post.creator.username}},
    ]


@pytest.mark.django_db
def test_get_post_list_filter_not_own_posts(api_client_with_credentials: APIClientWithUser) -> None:
    PostFactory(creator=api_client_with_credentials.user)
    post = PostFactory(creator=UserFactory())

    response = api_client_with_credentials.get(posts_url(query_kwargs={"is_creator": False}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {"text": post.text, "creator": {"id": post.creator.id, "username": post.creator.username}},
    ]


@pytest.mark.django_db
def test_get_post_detail_success(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory()

    response = api_client_with_credentials.get(posts_detail_url(post_id=post.pk))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "text": post.text,
        "creator": {"id": post.creator.id, "username": post.creator.username},
    }


@pytest.mark.django_db
def test_get_post_detail_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    response = api_client_with_credentials.get(posts_detail_url(post_id=0))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_post_success(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory(text="old post content", creator=api_client_with_credentials.user)

    response = api_client_with_credentials.patch(posts_detail_url(post_id=post.pk), data={"text": "new post content"})
    post.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert post.text == "new post content"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "text, expected_response_json",
    [
        (
            "test",
            {"text": ["Ensure this value has at least 10 characters (it has 4)."]},
        ),
        (
            1001 * "a",
            {"text": ["Ensure this value has at most 1000 characters (it has 1001)."]},
        ),
    ],
)
def test_update_post_validation_failed(
    api_client_with_credentials: APIClientWithUser,
    text: str,
    expected_response_json: Dict[str, List[str]],
) -> None:
    board = BoardFactory()
    board.members.add(api_client_with_credentials.user)
    post = PostFactory(text="old post content", creator=api_client_with_credentials.user)

    response = api_client_with_credentials.patch(posts_detail_url(post_id=post.pk), data={"text": text})
    post.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_response_json  # type: ignore[attr-defined]
    assert post.text == "old post content"


@pytest.mark.django_db
def test_update_post_by_non_creator(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory(text="old post content", creator=UserFactory())

    response = api_client_with_credentials.patch(posts_detail_url(post_id=post.pk), data={"text": "new post content"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {  # type: ignore[attr-defined]
        "detail": "Only post creators can edit posts. You are not a creator of this post."
    }


@pytest.mark.django_db
def test_update_post_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    response = api_client_with_credentials.patch(posts_detail_url(post_id=0), data={"text": "new post content"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_post_success(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory(creator=api_client_with_credentials.user)

    response = api_client_with_credentials.delete(posts_detail_url(post_id=post.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db
def test_delete_post_by_non_creator(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory(creator=UserFactory())

    response = api_client_with_credentials.delete(posts_detail_url(post_id=post.id))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db
def test_delete_post_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    response = api_client_with_credentials.delete(posts_detail_url(post_id=0))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_comment_success(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory()
    post.board.members.add(api_client_with_credentials.user)

    response = api_client_with_credentials.post(comments_url(), {"text": "test test test", "post": post.id})

    assert response.status_code == status.HTTP_201_CREATED
    assert Comment.objects.count() == 1

    comment = Comment.objects.first()

    assert comment.creator == api_client_with_credentials.user  # type: ignore
    assert comment.post == post  # type: ignore
    assert comment.parent is None  # type: ignore


@pytest.mark.django_db
def test_create_comment_reply_success(api_client_with_credentials: APIClientWithUser) -> None:
    comment_parent = CommentFactory()
    comment_parent.post.board.members.add(api_client_with_credentials.user)

    response = api_client_with_credentials.post(
        comments_url(), {"text": "test test test", "post": comment_parent.post.id, "parent": comment_parent.id}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Comment.objects.count() == 2

    comment = Comment.objects.last()

    assert comment.creator == api_client_with_credentials.user  # type: ignore
    assert comment.post == comment_parent.post  # type: ignore
    assert comment.parent == comment_parent  # type: ignore


@pytest.mark.django_db
@pytest.mark.parametrize(
    "text, expected_response_json",
    [
        (
            "",
            {"text": ["This field may not be blank."]},
        ),
        (
            1001 * "a",
            {"text": ["Ensure this value has at most 1000 characters (it has 1001)."]},
        ),
    ],
)
def test_create_comment_validation_failed(
    api_client_with_credentials: APIClientWithUser,
    text: str,
    expected_response_json: Dict[str, List[str]],
) -> None:
    post = PostFactory()
    post.board.members.add(api_client_with_credentials.user)

    response = api_client_with_credentials.post(comments_url(), {"text": text, "post": post.id})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == expected_response_json  # type: ignore[attr-defined]
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_cannot_create_comment_if_not_a_board_member(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory()

    response = api_client_with_credentials.post(comments_url(), {"text": "test test test", "post": post.id})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {  # type: ignore
        "board": ["Only board members can add comments. You are not a member of this board."]
    }


@pytest.mark.django_db
def test_cannot_create_comment_if_parent_does_not_belong_to_post_given(
    api_client_with_credentials: APIClientWithUser,
) -> None:
    post = PostFactory()
    post.board.members.add(api_client_with_credentials.user)
    parent = CommentFactory()

    response = api_client_with_credentials.post(
        comments_url(), {"text": "test test test", "post": post.id, "parent": parent.id}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"parent": ["The parent comment does not belong to the post specified."]}  # type: ignore


@pytest.mark.django_db
def test_get_comment_list(api_client_with_credentials: APIClientWithUser) -> None:
    comment_1 = CommentFactory()
    comment_2 = CommentFactory()

    response = api_client_with_credentials.get(comments_url())

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2
    assert response.json()["results"] == [
        {
            "text": comment_1.text,
            "creator": {
                "id": comment_1.creator.id,
                "username": comment_1.creator.username,
            },
            "parent_id": None,
        },
        {
            "text": comment_2.text,
            "creator": {"id": comment_2.creator.id, "username": comment_2.creator.username},
            "parent_id": None,
        },
    ]


@pytest.mark.django_db
def test_get_comment_list_filter_by_text(api_client_with_credentials: APIClientWithUser) -> None:
    comment = CommentFactory(text="Text that I am looking for")
    CommentFactory(text="Something unimportant")

    response = api_client_with_credentials.get(comments_url(query_kwargs={"text": "I am looking"}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {
            "text": comment.text,
            "creator": {"id": comment.creator.id, "username": comment.creator.username},
            "parent_id": comment.parent,
        }
    ]


@pytest.mark.django_db
def test_get_comment_list_filter_by_post(api_client_with_credentials: APIClientWithUser) -> None:
    comment = CommentFactory(text="Text that I am looking for")
    CommentFactory(text="Something unimportant")

    response = api_client_with_credentials.get(comments_url(query_kwargs={"post": comment.post.id}))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {
            "text": comment.text,
            "creator": {"id": comment.creator.id, "username": comment.creator.username},
            "parent_id": comment.parent,
        }
    ]


@pytest.mark.django_db
def test_get_comment_list_filter_by_parent(api_client_with_credentials: APIClientWithUser) -> None:
    post = PostFactory()
    comment = CommentFactory(text="Text that I am looking for", parent=CommentFactory(post=post), post=post)
    CommentFactory(text="Something unimportant", post=post)

    response = api_client_with_credentials.get(
        comments_url(query_kwargs={"post": post.id, "parent": comment.parent.id})
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"] == [
        {
            "text": comment.text,
            "creator": {"id": comment.creator.id, "username": comment.creator.username},
            "parent_id": comment.parent_id,
        }
    ]


@pytest.mark.django_db
def test_get_comment_detail_success(api_client_with_credentials: APIClientWithUser) -> None:
    comment = CommentFactory()

    response = api_client_with_credentials.get(comments_detail_url(comment_id=comment.pk))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "text": comment.text,
        "creator": {"id": comment.creator.id, "username": comment.creator.username},
        "parent_id": comment.parent_id,
    }


@pytest.mark.django_db
def test_get_comment_detail_not_found(api_client_with_credentials: APIClientWithUser) -> None:
    response = api_client_with_credentials.get(comments_detail_url(comment_id=0))

    assert response.status_code == status.HTTP_404_NOT_FOUND
