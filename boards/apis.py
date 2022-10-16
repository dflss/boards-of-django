from typing import Any, cast

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from boards.selectors import board_get, board_list
from boards.services import create_board


class BoardsApi(APIView):
    """Manage boards."""

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=True)

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description=""),
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new board.

        Input is considered valid when:
        - the name is unique
        - the name contains only small/big letters (a-z) and underscore (_)
        - the name is at least 3 and at maximum 20 characters long

        Returns
        -------
        HTTP response with code:
        - 201 if board was successfully created
        - 400 if input validation failed
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_board(**serializer.validated_data, creator=cast(User, request.user))

        return Response(status=status.HTTP_201_CREATED)

    class FilterSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=False)
        is_member = serializers.BooleanField(required=False)
        is_admin = serializers.BooleanField(required=False)

    class OutputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=True)

    @swagger_auto_schema(responses={200: OutputSerializer(many=True)})  # type: ignore
    def get(self, request: Request) -> Response:
        """
        Retrieve list of boards.

        Returns
        -------
        HTTP response with code 200
        """
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        boards = board_list(**filters_serializer.validated_data, user=cast(User, request.user))

        data = self.OutputSerializer(boards, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)


class DetailBoardsApi(APIView):
    """View board details."""

    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=True)

    @swagger_auto_schema(responses={200: OutputSerializer()})  # type: ignore
    def get(self, request: Request, board_id: int) -> Response:
        """
        Retrieve board details.

        Returns
        -------
        HTTP response with code:
        - 200 if board was found
        - 404 if board does not exist
        """
        board = board_get(board_id=board_id)
        if board is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = self.OutputSerializer(board).data

        return Response(data=data, status=status.HTTP_200_OK)
