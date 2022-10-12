from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.services import create_user

User = get_user_model()


class UserRegisterApi(APIView):
    """Create a new user."""

    class InputSerializer(serializers.Serializer[Any]):
        email = serializers.EmailField(required=True)
        username = serializers.CharField(required=True)
        password = serializers.CharField(required=True)
        password2 = serializers.CharField(required=True)

    def post(self, request: Request) -> Response:
        """
        Create a new user.

        Input is considered valid when:
        - the password is non-trivial
        - both passwords are equal
        - e-mail format is correct
        - e-mail is unique
        - username is unique

        Parameters
        ----------
        request : User's request

        Returns
        -------
        HTTP response with code:
        - 201 if user was successfully created
        - 400 if input validation failed
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_user(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class UserLoginApi(ObtainAuthToken):
    """Provide authorization token."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create authorization token and assign it to the user.

        The user must provide correct credentials (username and password).

        Parameters
        ----------
        request : User's request. Data must contain username and password.

        Returns
        -------
        HTTP response with code:
        - 201 if credentials were correct and token was created
        - 400 if credentials were incorrect

        Response body:
        - token : authorization token that was created
        """
        response = super().post(request, *args, **kwargs)

        return response


class UserLogoutApi(APIView):
    """Delete authorization token that is attached to this request."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """Delete authorization token that is attached the user making request.

        Parameters
        ----------
        request : User's request

        Returns
        -------
        Empty HTTP response with code 200.
        """
        user = request.user
        if hasattr(user, "auth_token"):
            user.auth_token.delete()  # type: ignore[union-attr]

        response = Response()

        return response
