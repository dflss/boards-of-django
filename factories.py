from typing import List

import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from factory import Faker, SubFactory, fuzzy

from authentication.models import ConfirmationToken
from authentication.models import User as UserType
from boards.models import Board, Comment, Post

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda n: f"{n.username}@example.com".lower())
    password = factory.LazyFunction(lambda: make_password("password"))


class ConfirmationTokenFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = ConfirmationToken

    user = SubFactory(UserFactory)
    token = fuzzy.FuzzyText()


class BoardFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = Board

    name = factory.Sequence(lambda n: f"board_{n}")

    @factory.post_generation  # type: ignore
    def members(self, create: bool, extracted: List[UserType]) -> None:
        if not create:
            return
        if extracted:
            self.members.add(*extracted)

    @factory.post_generation  # type: ignore
    def admins(self, create: bool, extracted: List[UserType]) -> None:
        if not create:
            return
        if extracted:
            self.admins.add(*extracted)


class PostFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = Post

    text = Faker("sentence")
    creator = SubFactory(UserFactory)
    board = SubFactory(BoardFactory)


class CommentFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = Comment

    text = Faker("sentence")
    creator = SubFactory(UserFactory)
    post = SubFactory(PostFactory)
