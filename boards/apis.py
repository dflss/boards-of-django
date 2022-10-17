from typing import Any

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from boards.selectors import board_get, board_list
from boards.services import add_admin_to_board, add_member_to_board, create_board
from common.utils import RequestWithUser as Request


class BoardsApi(APIView):
    """Manage boards."""

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=True)

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description="board was successfully created"),
            400: openapi.Response(description="input validation failed"),
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new board.

        Input is considered valid when:
        - the name is unique
        - the name contains only small/big letters (a-z) and underscore (_)
        - the name is at least 3 and at maximum 20 characters long
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_board(**serializer.validated_data, creator=request.user)

        return Response(status=status.HTTP_201_CREATED)

    class FilterSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=False)
        is_member = serializers.BooleanField(required=False)
        is_admin = serializers.BooleanField(required=False)

    class OutputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=True)

    @swagger_auto_schema(responses={200: OutputSerializer(many=True)})  # type: ignore
    def get(self, request: Request) -> Response:
        """Retrieve list of boards."""
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        boards = board_list(**filters_serializer.validated_data, user=request.user)

        data = self.OutputSerializer(boards, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)


class DetailBoardsApi(APIView):
    """View board details."""

    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=True)

    @swagger_auto_schema(
        responses={
            200: OutputSerializer(),
            404: openapi.Response(description="board does not exist"),
        }
    )  # type: ignore
    def get(self, request: Request, board_id: int) -> Response:
        """Retrieve board details."""
        board = board_get(board_id=board_id)
        if board is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = self.OutputSerializer(board).data

        return Response(data=data, status=status.HTTP_200_OK)


class JoinBoardsApi(APIView):
    """Join the board as its member."""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, board_id: int) -> Response:
        """
        Join the board as its member.

        If the user is already a board member, nothing happens and 200 is returned.

        Returns
        -------
        HTTP response with code:
        - 200 if board was found
        - 404 if board does not exist
        """
        board = board_get(board_id=board_id)
        if board is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = request.user
        add_member_to_board(board=board, user=user)
        return Response(status=status.HTTP_200_OK)


class AddAdminsBoardsApi(APIView):
    """Assign users as board administrators."""

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer[Any]):
        users_to_add = serializers.PrimaryKeyRelatedField(required=True, many=True, queryset=User.objects.all())

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            200: openapi.Response(description="users were assigned as admins"),
            403: openapi.Response(description="user making the request is not a board admin"),
            404: openapi.Response(description="board does not exist"),
        },
    )
    def post(self, request: Request, board_id: int) -> Response:
        """
        Assign users as board administrators.

        This action can only be performed by a current board admin. If the user to add is already an admin, nothing
        happens and 200 is returned. If a user to add is not a board member, she/he is cannot be added as an admin.
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = board_get(board_id=board_id)
        if board is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = request.user

        add_admin_to_board(**serializer.validated_data, board=board, user=user)
        return Response(status=status.HTTP_200_OK)
