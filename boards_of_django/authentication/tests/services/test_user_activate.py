import re
from datetime import timedelta

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from pytest_mock import MockerFixture

from boards_of_django.authentication.services import activate_user
from factories import ConfirmationOTPFactory, UserFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_active",
    [True, False],
)
def test_user_is_active_after_activation(is_active: bool) -> None:
    user = UserFactory(is_active=is_active)
    confirmation_otp = ConfirmationOTPFactory(user=user)

    activate_user(email=user.email, otp=confirmation_otp.otp)

    user.refresh_from_db()

    assert user.is_active


@pytest.mark.django_db
def test_raise_exception_if_user_does_not_exist() -> None:
    confirmation_otp = ConfirmationOTPFactory()

    with pytest.raises(ValidationError, match=re.escape("{'email': ['Email is invalid.']}")):
        activate_user(email="wrong@example.com", otp=confirmation_otp.otp)


@pytest.mark.django_db
def test_raise_exception_if_otp_is_invalid() -> None:
    user = UserFactory(is_active=False)
    confirmation_otp = ConfirmationOTPFactory()

    with pytest.raises(ValidationError, match=re.escape("{'otp': ['One-time password is invalid.']}")):
        activate_user(email=user.email, otp=confirmation_otp.otp)

    user.refresh_from_db()

    assert not user.is_active


@pytest.mark.django_db
def test_raise_exception_if_otp_is_expired(mocker: MockerFixture) -> None:
    user = UserFactory(is_active=False)
    confirmation_otp = ConfirmationOTPFactory(user=user)
    mocker.patch(
        "boards_of_django.authentication.services.now",
        return_value=confirmation_otp.created_at
        + timedelta(seconds=int(settings.CONFIRMATION_OTP_VALID_FOR_SECONDS) + 1),
    )

    with pytest.raises(ValidationError, match=re.escape("{'otp': ['One-time password is invalid.']}")):
        activate_user(email=user.email, otp=confirmation_otp.otp)

    user.refresh_from_db()

    assert not user.is_active
