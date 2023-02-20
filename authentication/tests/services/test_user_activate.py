import pytest

from authentication.services import activate_user
from factories import ConfirmationTokenFactory, UserFactory


@pytest.mark.django_db
def test_user_becomes_active_after_activation() -> None:
    user = UserFactory(is_active=False)
    confirmation_token = ConfirmationTokenFactory(user=user)

    activate_user(token=confirmation_token.token)

    user.refresh_from_db()

    assert user.is_active
