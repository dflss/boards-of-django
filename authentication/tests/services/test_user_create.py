import pytest

from authentication.models import ConfirmationToken
from authentication.services import create_user


@pytest.mark.django_db
def test_user_is_created_inactive() -> None:
    user = create_user(
        email="test@example.com", username="test", password="strongPassword!", password2="strongPassword!"
    )

    assert not user.is_active


@pytest.mark.django_db
def test_when_creating_user_confirmation_token_is_created() -> None:
    user = create_user(
        email="test@example.com", username="test", password="strongPassword!", password2="strongPassword!"
    )

    assert ConfirmationToken.objects.count() == 1
    assert ConfirmationToken.objects.first() is not None
    assert ConfirmationToken.objects.first().user == user
