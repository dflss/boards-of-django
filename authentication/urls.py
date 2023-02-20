from django.urls import path

from authentication.apis import UserConfirmRegistrationApi, UserLoginApi, UserLogoutApi, UserRegisterApi

urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="register"),
    path("confirm-registration/", UserConfirmRegistrationApi.as_view(), name="confirm-registration"),
    path("login/", UserLoginApi.as_view(), name="login"),
    path("logout/", UserLogoutApi.as_view(), name="logout"),
]
