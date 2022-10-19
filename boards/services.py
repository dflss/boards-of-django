from typing import List

from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

from authentication.models import User
from boards.models import Board, Post


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
