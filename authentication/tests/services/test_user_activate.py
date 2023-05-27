import pytest

from authentication.services import activate_user
from factories import ConfirmationOTPFactory, UserFactory


@pytest.mark.django_db
def test_user_becomes_active_after_activation() -> None:
    user = UserFactory(is_active=False)
    confirmation_otp = ConfirmationOTPFactory(user=user)

    activate_user(email=user.email, otp=confirmation_otp.otp)

    user.refresh_from_db()

    assert user.is_active
