from django.core.exceptions import ValidationError
from django.db.models import QuerySet

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


def add_admin_to_board(*, board: Board, users_to_add: QuerySet[User]) -> None:
    """
    Ensure that the user is added to a board as its admin.

    Parameters
    ----------
    board : Board that the users will be added to as admins.
    users_to_add : : Users that will join as admins.

    Returns
    -------
    None
    """
    user_ids = [user.id for user in users_to_add]
    users_to_add = User.objects.filter(id__in=user_ids)
    board.admins.add(*users_to_add)
