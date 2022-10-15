from django.core.exceptions import ValidationError

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
