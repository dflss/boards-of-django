from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from authentication.models import ConfirmationToken, User


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
    is_active: bool = False,
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

    create_confirmation_token(user=user)

    return user


def activate_user(*, token: str) -> None:
    """
    Activate user's account after a correct confirmation token is provided.

    Parameters
    ----------
    token : String value of the token

    Returns
    -------
    None

    """
    confirmation_token = ConfirmationToken.objects.filter(token=token).first()

    if confirmation_token is None:
        raise ValidationError({"token": "Token is invalid."})

    user = confirmation_token.user
    user.is_active = True
    user.save()


def create_confirmation_token(*, user: User) -> ConfirmationToken:
    """
    Create a new confirmation token instance and save it in database.

    Parameters
    ----------
    user : User assigned to the token

    Returns
    -------
    Confirmation token

    """
    confirmation_token = ConfirmationToken(user=user)
    confirmation_token.full_clean()
    confirmation_token.save()

    return confirmation_token
