from typing import List

from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

from authentication.models import User
from boards.models import Board


def _validate_board_name(*, name: str) -> None:
    if len(name) < 3:
        raise ValidationError({"name": "Board name cannot be shorter than 3 characters."})
    if len(name) > 20:
        raise ValidationError({"name": "Board name cannot be longer than 20 characters."})
    for char in name:
        if not (char.isalpha() or char == "_"):
            raise ValidationError(
                {"name": "Board name can only contain alphabet letters (a-z) and underscore (_) character."}
            )


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
    _validate_board_name(name=name)

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
