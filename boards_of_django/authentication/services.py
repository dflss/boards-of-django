from datetime import timedelta

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from boards_of_django.authentication.models import ConfirmationOTP, User
from boards_of_django.tasks.celery import task_send_confirmation_email


def _validate_user_password(*, password: str, password2: str) -> None:
    if password != password2:
        raise ValidationError({"password": "Passwords do not match."})
    try:
        validate_password(password=password)
    except ValidationError as e:
        raise ValidationError({"password": e}) from e


def _validate_user_username(*, username: str) -> None:
    if len(username) < 3:  # noqa: PLR2004
        raise ValidationError({"username": "Username cannot be shorter than 3 characters."})
    if len(username) > 20:  # noqa: PLR2004
        raise ValidationError({"username": "Username cannot be longer than 20 characters."})


def _create_confirmation_otp_and_send_email(user: User) -> None:
    confirmation_otp = ConfirmationOTP(user=user)
    confirmation_otp.full_clean()
    confirmation_otp.save()

    task_send_confirmation_email(user, confirmation_otp)


def create_user(  # noqa: PLR0913
    *,
    email: str,
    username: str,
    is_active: bool = False,
    is_admin: bool = False,
    password: str,
    password2: str,
) -> User:
    """Create a new user instance and save it in database.

    Before creation, password and username will be validated.
    Passwords must match and pass the default Django password validation. Username must contain 3-20 characters.

    Parameters
    ----------
    email : User's email address
    username : User's username
    is_active : Indicates if user is active. Initially, when the user is created, this will be set to False. The user
        becomes active after activating account using OTP sent to email used for registration.
    is_admin : Indicates if user has administrative privileges
    password : User's password
    password2 : Password confirmation

    Returns:
    -------
    User

    """
    _validate_user_password(password=password, password2=password2)
    _validate_user_username(username=username)

    user = User.objects.create_user(
        email=email, username=username, is_active=is_active, is_admin=is_admin, password=password
    )

    _create_confirmation_otp_and_send_email(user=user)

    return user


def activate_user(*, email: str, otp: str) -> None:
    """Activate user's account after a correct confirmation OTP is provided.

    Parameters
    ----------
    email: Email address of the user whose account is to be verified
    otp : One-time password to activate user's account

    Returns:
    -------
    None

    """
    user = User.objects.filter(email=email).first()
    if user is None:
        raise ValidationError({"email": "Email is invalid."})

    confirmation_otp = ConfirmationOTP.objects.filter(user=user, otp=otp).first()

    if confirmation_otp is None or (
        confirmation_otp.created_at + timedelta(seconds=int(settings.CONFIRMATION_OTP_VALID_FOR_SECONDS)) < now()
    ):
        raise ValidationError({"otp": "One-time password is invalid."})

    user.is_active = True
    user.save()


def resend_confirmation_email(email: str) -> None:
    """Resend a confirmation email.

    Parameters
    ----------
    email : Email address to resend the email to.

    Returns:
    -------
    None

    """
    user = User.objects.get(email=email)
    ConfirmationOTP.objects.filter(user=user).delete()

    _create_confirmation_otp_and_send_email(user=user)
