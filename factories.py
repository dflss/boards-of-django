import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):  # type: ignore
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda n: "{}@example.com".format(n.username).lower())
    password = factory.LazyFunction(lambda: make_password("password"))
