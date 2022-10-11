from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from common.models import BaseModel


class UserManager(BaseUserManager["User"]):
    """Manage class User.

    Contains methods that run validation and create users.
    """

    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        is_active: bool = True,
        is_admin: bool = False,
    ) -> "User":
        """Save user instance in database.

        Keyword parameters:
        email -- user's email address
        username -- user's username
        password -- user's password
        is_active -- indicates if user is active
        is_admin -- indicates if user has administrative privileges
        """
        if not email:
            raise ValueError("Users must have an email address")

        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email.lower()), username=username, is_active=is_active, is_admin=is_admin
        )

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, username: str, password: str) -> "User":
        """Save superuser instance in database.

        Keyword parameters:
        email -- user's email address
        username -- user's username
        password -- user's password
        """
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            is_active=True,
            is_admin=True,
        )

        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Custom User model.

    Attributes:
    email -- user's email address
    username -- user's username
    is_active -- indicates if user is active
    is_admin -- indicates if user has administrative privileges
    """

    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        verbose_name="username",
        max_length=255,
        unique=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self) -> str:
        return self.email

    def is_staff(self) -> bool:
        """Return True if user is admin."""
        return self.is_admin
