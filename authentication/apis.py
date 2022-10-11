from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers, status
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
        """Create a new user.

        Return
        - 201 if user was successfully created
        - 400 if input validation failed.
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_user(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)
