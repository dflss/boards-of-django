from typing import Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from authentication.models import User
from boards.models import Board, Comment, Post
from common.services import model_update


def create_board(
    *,
    name: str,
    creator: User,
) -> Board:
    """
    Create a new board instance and save it in database.

    Before creation, board name be validated.
    Name must contain 3-20 characters and consist only of letters (a-z) and underscore (_) character.
    The user who created the board will automatically be added as both member and admin of the board.

    Parameters
    ----------
    name : Board's name
    creator : User that created the board

    Returns
    -------
    Board

    """
    board = Board(name=name)
    board.full_clean()
    board.save()

    board.members.add(creator)
    board.admins.add(creator)

    return board


def add_member_to_board(
    *,
    board: Board,
    user: User,
) -> None:
    """
    Ensure that the user is added to a board as its member.

    Parameters
    ----------
    board : Board that the user will be added to as member.
    user : User that will join as member.

    Returns
    -------
    None
    """
    board.members.add(user)


def add_admin_to_board(*, board: Board, user: User, users_to_add: List[User]) -> None:
    """
    Add users to a board as its admins.

    If a user to add is already an admin, nothing happens. The user to add must be a board member. The adding user
    must be a board admin.

    Parameters
    ----------
    board : Board that the users will be added to as admins.
    user : user who is performing the action of adding new admins
    users_to_add : Users that will be added as admins.

    Returns
    -------
    None
    """
    if user not in board.admins.all():
        raise PermissionDenied("Only board admin can perform this action.")

    if board.members.filter(id__in=[user.id for user in users_to_add]).count() != len(users_to_add):
        raise ValidationError({"users_to_add": "Only board members can be added as board admins."})

    board.admins.add(*users_to_add)


def create_post(*, text: str, creator: User, board: Board) -> Post:
    """
    Create a new post instance and save it in database.

    Before creation, post content be validated. Text must contain 10-1000 characters. The user must be a board member
    to create a post.

    Parameters
    ----------
    text : Post's content
    creator : User that created the post
    board: Board where the post will be added

    Returns
    -------
    Post

    """
    if creator not in board.members.all():
        raise ValidationError({"board": "Only board members can add posts. You are not a member of this board."})

    post = Post(text=text, creator=creator, board=board)
    post.full_clean()
    post.save()

    return post


@transaction.atomic
def update_post(*, post: Post, data: Dict[str, Any], user: User) -> Post:
    """
    Update a post.

    Parameters
    ----------
    post : Post to update
    data: Fields to update and their values
    user: User that initiates post edition

    Returns
    -------
    Post

    """
    if user != post.creator:
        raise PermissionDenied("Only post creators can edit posts. You are not a creator of this post.")

    post, has_updated = model_update(instance=post, fields=["text"], data=data)

    if has_updated:
        post.edited = True
        post.save()

    return post


@transaction.atomic
def delete_post(*, post: Post, user: User) -> Post:
    """
    Update a post.

    Parameters
    ----------
    post : Post to update
    user: User that initiates post deletion

    Returns
    -------
    Post

    """
    if user != post.creator:
        raise PermissionDenied("Only post creators can delete posts. You are not a creator of this post.")

    post.delete()

    return post


def create_comment(*, text: str, creator: User, post: Post, parent: Optional[Comment] = None) -> Comment:
    """
    Create a new comment instance and save it in database.

    Before creation, comment content be validated. Text must contain 1-1000 characters. The user must be a board member
    to create a comment.

    Parameters
    ----------
    text : Post's content
    creator : User that creates the comment
    post: Post which is being commented
    parent: Comment which is being replied to

    Returns
    -------
    Post
    """
    if creator not in post.board.members.all():
        raise ValidationError({"board": "Only board members can add comments. You are not a member of this board."})

    if parent is not None and parent.post != post:
        raise ValidationError({"parent": "The parent comment does not belong to the post specified."})

    comment = Comment(text=text, creator=creator, post=post, parent=parent)
    comment.full_clean()
    comment.save()

    return comment
