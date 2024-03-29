from typing import Optional

from django.db.models import Q
from django.db.models.query import QuerySet

from boards_of_django.authentication.models import User
from boards_of_django.boards.models import Board, Comment, Post


def board_list(
    *, user: User, name: Optional[str] = None, is_member: Optional[bool] = None, is_admin: Optional[bool] = None
) -> QuerySet[Board]:
    """Fetch list of boards for the given user.

    Parameters
    ----------
    user : Given user
    name : Only boards that contain this name will be returned
    is_admin : If set to True, only boards that the given user administers will be returned. If set to False, the
        boards that are NOT administered by the given user will be returned.
    is_member : If set to True, only boards that the given user is a member of will be returned. If set to False, the
        boards that the user is NOT a member of will be returned.

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


def post_list(
    *, user: User, board: Optional[Board] = None, text: Optional[str] = None, is_creator: Optional[bool] = None
) -> QuerySet[Post]:
    """Fetch list of posts for the given user.

    Parameters
    ----------
    user: Given user
    board : Board to which the posts belong
    text : The text that the post contains
    is_creator : If set to True, only the posts that the given user created will be shown. When set to false, all
        posts that were NOT created by the given user will be shown

    Returns
    -------
    Filtered post queryset.
    """
    qs = Post.objects.all()
    if board is not None:
        qs = qs.filter(board=board)
    if text is not None:
        qs = qs.filter(text__icontains=text)
    if is_creator is not None:
        if is_creator:
            qs = qs.filter(creator=user)
        else:
            qs = qs.filter(~Q(creator=user))

    return qs.order_by("-id")


def post_get(*, post_id: int) -> Optional[Post]:
    """Get the post instance with given id.

    Parameters
    ----------
    post_id : Post's pk.

    Returns
    -------
    Post's instance or None if the post does not exist.
    """
    return Post.objects.filter(id=post_id).first()


def comment_list(
    *, text: Optional[str] = None, post: Optional[Post] = None, parent: Optional[Comment] = None
) -> QuerySet[Comment]:
    """Fetch a filtered list of comments.

    Parameters
    ----------
    text : The text that the comment contains
    post : Post to which the comments belong
    parent : The comment whose replies should be returned. If no parent is provided, by default only root comments
        (those that are not replies to any other comment) are returned.

    Returns
    -------
    Filtered comment queryset.
    """
    qs = Comment.objects.all()
    if text is not None:
        qs = qs.filter(text__icontains=text)
    if post is not None:
        qs = qs.filter(post=post)
    if parent is not None:
        qs = qs.filter(parent=parent)
    else:
        qs = qs.filter(parent__isnull=True)

    return qs.order_by("id")


def comment_get(*, comment_id: int) -> Optional[Comment]:
    """Get the comment instance with given id.

    Parameters
    ----------
    comment_id : Comment's pk.

    Returns
    -------
    Comment's instance or None if the comment does not exist.
    """
    return Comment.objects.filter(id=comment_id).first()
