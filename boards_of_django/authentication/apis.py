from typing import Any

from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_of_django.authentication.services import activate_user, create_user, resend_confirmation_email

User = get_user_model()


class UserRegisterApi(APIView):
    """Create a new user."""

    class InputSerializer(serializers.Serializer[Any]):
        email = serializers.EmailField(required=True)
        username = serializers.CharField(required=True)
        password = serializers.CharField(required=True)
        password2 = serializers.CharField(required=True)

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description="user was successfully created"),
            400: openapi.Response(description="input validation failed"),
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new user.

        Input is considered valid when:
        - the password is non-trivial
        - both passwords are equal
        - e-mail format is correct
        - e-mail is unique
        - username is unique
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_user(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class UserConfirmRegistrationApi(APIView):
    """Confirm registration of a user."""

    class InputSerializer(serializers.Serializer[Any]):
        email = serializers.EmailField(required=True)
        otp = serializers.CharField(required=True)

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description="user registration was successfully confirmed"),
            400: openapi.Response(description="input validation failed"),
        },
    )
    def post(self, request: Request) -> Response:
        """Confirm registration of a user."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        activate_user(**serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class UserResendConfirmationOTPApi(APIView):
    """Resend confirmation email."""

    class InputSerializer(serializers.Serializer[Any]):
        email = serializers.EmailField(required=True)

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description="confirmation email was successfully resent"),
            400: openapi.Response(description="input validation failed"),
        },
    )
    def post(self, request: Request) -> Response:
        """Resend confirmation email."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resend_confirmation_email(**serializer.validated_data)

        return Response(status=status.HTTP_200_OK)


class UserLoginApi(ObtainAuthToken):
    """Log the user in."""

    @swagger_auto_schema(  # type: ignore
        request_body=AuthTokenSerializer,
        responses={
            201: openapi.Response(
                description="",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"token": openapi.Schema(type=openapi.TYPE_STRING, description="authorization token")},
                ),
            ),
            400: openapi.Response(description="incorrect credentials"),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Log the user in by creating an authorization token and assigning it to the user.

        The user must provide correct credentials (username and password). In response, the user receives a token
        which can be later used via Authorization: Token <token> header to authenticate to auth-protected endpoints.
        """
        return super().post(request, *args, **kwargs)


class UserLogoutApi(APIView):
    """Log the user out."""

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(  # type: ignore
        responses={
            200: openapi.Response(description=""),
        },
    )
    def post(self, request: Request) -> Response:
        """Log the user out by invalidating her/his authorization token."""
        user = request.user
        if hasattr(user, "auth_token"):
            user.auth_token.delete()  # type: ignore

        return Response(status=status.HTTP_200_OK)
