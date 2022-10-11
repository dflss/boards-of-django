from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from authentication.models import User


def _validate_user_password(*, password: str, password2: str) -> None:
    if password != password2:
        raise ValidationError({"password": "Passwords do not match."})
    try:
        validate_password(password=password)
    except ValidationError as e:
        raise ValidationError({"password": e}) from e


def _validate_user_username(*, username: str) -> None:
    if len(username) < 3:
        raise ValidationError({"username": "Username cannot be shorter than 3 characters."})
    if len(username) > 20:
        raise ValidationError({"username": "Username cannot be longer than 20 characters."})


def create_user(
    *,
    email: str,
    username: str,
    is_active: bool = True,
    is_admin: bool = False,
    password: str,
    password2: str,
) -> User:
    """
    Create a new user instance and save it in database.

    Before creation, password and username will be validated.
    Passwords must match and pass the default Django password validation. Username must contain 3-20 characters.

    Parameters
    ----------
    email : User's email address
    username : User's username
    is_active : Indicates if user is active
    is_admin : Indicates if user has administrative privileges
    password : User's password
    password2 : Password confirmation

    Returns
    -------
    User

    """
    _validate_user_password(password=password, password2=password2)
    _validate_user_username(username=username)

    user = User.objects.create_user(
        email=email, username=username, is_active=is_active, is_admin=is_admin, password=password
    )

    return user
