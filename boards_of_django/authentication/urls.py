from django.urls import path

from boards_of_django.authentication.apis import (
    UserConfirmRegistrationApi,
    UserLoginApi,
    UserLogoutApi,
    UserRegisterApi,
    UserResendConfirmationOTPApi,
)

urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="register"),
    path("confirm-registration/", UserConfirmRegistrationApi.as_view(), name="confirm-registration"),
    path("resend-confirmation-token/", UserResendConfirmationOTPApi.as_view(), name="resend-confirmation-token"),
    path("login/", UserLoginApi.as_view(), name="login"),
    path("logout/", UserLogoutApi.as_view(), name="logout"),
]
