from typing import Optional

from django.db.models import Q
from django.db.models.query import QuerySet

from authentication.models import User
from boards.models import Board


def board_list(
    *, user: User, name: Optional[str] = None, is_member: Optional[bool] = None, is_admin: Optional[bool] = None
) -> QuerySet[Board]:
    """Fetch list of boards based on parameters provided.

    Parameters
    ----------
    user : User that is treated as a reference point when filtering the query by is_admin and is_member parameters
    name : Filter boards that contain the given name
    is_admin : Filter boards that the user administers
    is_member : Filter boards that the user is member of

    Returns
    -------
    Filtered board queryset.
    """
    qs = Board.objects.all()
    if name is not None:
        qs = qs.filter(name__icontains=name)
    if is_member is not None:
        if is_member:
            qs = qs.filter(members__in=[user])
        else:
            qs = qs.filter(~Q(members__in=[user]))
    if is_admin is not None:
        if is_admin:
            qs = qs.filter(admins__in=[user])
        else:
            qs = qs.filter(~Q(admins__in=[user]))

    return qs


def board_get(*, board_id: int) -> Optional[Board]:
    """Get the board instance with given id.

    Parameters
    ----------
    board_id : Board's pk.

    Returns
    -------
    Board's instance or None if the board does not exist.
    """
    return Board.objects.filter(id=board_id).first()
