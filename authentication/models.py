from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from common.models import TimestampedModel


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
        """
        Create and save user instance in database.

        Parameters
        ----------
        email : User's email address
        username : User's username
        password : User's password
        is_active : Indicates if user is active
        is_admin : Indicates if user has administrative privileges

        Returns
        -------
        User

        """
        if len(email) == 0:
            raise ValueError("Users must have an email address")

        if len(username) == 0:
            raise ValueError("Users must have a username")

        user = self.model(
            email=self.normalize_email(email.lower()), username=username, is_active=is_active, is_admin=is_admin
        )

        user.set_password(password)

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, username: str, password: str) -> "User":
        """
        Create and save superuser instance in database.

        Parameters
        ----------
        email : User's email address
        username : User's username
        password : User's password

        Returns
        -------
        User

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


class User(TimestampedModel, AbstractBaseUser, PermissionsMixin):
    """
    User model used across the app.

    Attributes
    ----------
    email : User's email address
    username : User's username
    is_active : Indicates if user is active
    is_admin : Indicates if user has administrative privileges
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
