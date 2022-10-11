from django.urls import include, path

from authentication.apis import UserRegisterApi

urlpatterns = [
    path(
        "auth/",
        include(
            (
                [
                    path("register/", UserRegisterApi.as_view(), name="register"),
                ],
                "auth",
            )
        ),
    ),
]
