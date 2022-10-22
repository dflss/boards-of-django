from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from common.models import TimestampedModel

User = get_user_model()


def _validate_contains_allowed_characters(name: str) -> None:
    for char in name:
        if not (char.isalpha() or char == "_"):
            raise ValidationError(
                [{"name": "Board name can only contain alphabet letters (a-z) and underscore (_) character."}]
            )


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

    name = models.CharField(
        unique=True, max_length=20, validators=[MinLengthValidator(3), _validate_contains_allowed_characters]
    )
    members = models.ManyToManyField(User, related_name="members")
    admins = models.ManyToManyField(User, related_name="admins")


class Post(TimestampedModel):
    """
    Post model.

    Posts are added to the board. Only board members can add new posts. All users can view all posts.

    Attributes
    ----------
    text : The post's content
    creator : User that created the post
    board : The board to which post was posted
    edited : A flag that indicates if a post was edited or not
    """

    text = models.TextField(validators=[MinLengthValidator(10), MaxLengthValidator(1000)])
    creator = models.ForeignKey(User, related_name="posts_created", on_delete=models.PROTECT)
    board = models.ForeignKey(Board, related_name="posts", on_delete=models.CASCADE)
    edited = models.BooleanField(default=False)
