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


def create_user(
    *,
    email: str,
    username: str,
    is_active: bool = True,
    is_admin: bool = False,
    password: str,
    password2: str,
) -> User:
    """Create a new user instance.

    Before creation, password will be validated. Passwords must match and pass the default Django password validation.
    """
    _validate_user_password(password=password, password2=password2)

    user = User.objects.create_user(
        email=email, username=username, is_active=is_active, is_admin=is_admin, password=password
    )

    return user
