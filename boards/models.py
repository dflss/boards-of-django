from django.contrib.auth import get_user_model
from django.db import models

from common.models import TimestampedModel

User = get_user_model()


class Board(TimestampedModel):
    """
    Board model.

    Board represents a board with a certain topic. Users can join a board to become members. They can also add posts
    and comments to the board.

    Attributes
    ----------
    name : Board's name
    members : Users that are members of the board
    admins : Users that are administrators of the board
    """

    name = models.CharField(unique=True, max_length=20)
    members = models.ManyToManyField(User, related_name="members")
    admins = models.ManyToManyField(User, related_name="admins")
