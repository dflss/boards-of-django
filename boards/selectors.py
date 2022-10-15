from typing import Any, Dict, Optional, cast

from django.db.models.query import QuerySet

from boards.filters import BoardFilter
from boards.models import Board


def board_list(*, filters: Optional[Dict[str, Any]] = None) -> QuerySet[Board]:
    """Fetch list of boards based on filters provided.

    Parameters
    ----------
    filters : Filters that should be applied to the board list.

    Returns
    -------
    Filtered board queryset.
    """
    filters = filters or {}

    qs = Board.objects.all()

    return cast(QuerySet[Board], BoardFilter(filters, qs).qs)


def board_get(*, board_id: int) -> Optional[Board]:
    """Get the board instance with given id.

    Parameters
    ----------
    board_id : Board's pk.

    Returns
    -------
    Board's instance or None if the board does not exist.
    """
    qs = Board.objects.filter(id=board_id)

    return qs.first()
