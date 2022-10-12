from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from authentication.apis import UserRegisterApi

urlpatterns = [
    path(
        "auth/",
        include(
            (
                [
                    path("register/", UserRegisterApi.as_view(), name="register"),
                    path("login/", obtain_auth_token, name="login"),
                ],
                "auth",
            )
        ),
    ),
]
