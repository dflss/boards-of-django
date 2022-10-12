from django.urls import include, path

from authentication.apis import UserLoginApi, UserLogoutApi, UserRegisterApi

urlpatterns = [
    path(
        "auth/",
        include(
            (
                [
                    path("register/", UserRegisterApi.as_view(), name="register"),
                    path("login/", UserLoginApi.as_view(), name="login"),
                    path("logout/", UserLogoutApi.as_view(), name="logout"),
                ],
                "auth",
            )
        ),
    ),
]
