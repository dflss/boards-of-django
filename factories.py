from typing import List

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from authentication.models import User as UserType
from boards.models import Board

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda n: f"{n.username}@example.com".lower())
    password = factory.LazyFunction(lambda: make_password("password"))


class BoardFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = Board

    name = factory.Sequence(lambda n: f"board_{n}")

    @factory.post_generation  # type: ignore
    def members(self, create: bool, extracted: List[UserType]) -> None:
        if not create:
            return
        if extracted:
            for member in extracted:
                self.members.add(member)

    @factory.post_generation  # type: ignore
    def admins(self, create: bool, extracted: List[UserType]) -> None:
        if not create:
            return
        if extracted:
            for admin in extracted:
                self.admins.add(admin)
