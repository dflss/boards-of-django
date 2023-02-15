from typing import Any

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from boards.models import Board, Comment, Post
from boards.selectors import board_get, board_list, comment_get, comment_list, post_get, post_list
from boards.services import (
    add_admin_to_board,
    add_member_to_board,
    create_board,
    create_comment,
    create_post,
    delete_post,
    update_post,
)
from common.pagination import LimitOffsetPagination, get_paginated_response
from common.utils import RequestWithUser as Request
from common.utils import inline_serializer


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

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer[Any]):
        name = serializers.CharField(required=False)
        is_member = serializers.BooleanField(required=False, allow_null=True, default=None)
        is_admin = serializers.BooleanField(required=False, allow_null=True, default=None)

    class OutputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField()

    @swagger_auto_schema(responses={200: OutputSerializer(many=True)})  # type: ignore
    def get(self, request: Request) -> Response:
        """Retrieve list of boards."""
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        boards = board_list(**filters_serializer.validated_data, user=request.user)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=boards,
            request=request,
            view=self,
        )


class DetailBoardsApi(APIView):
    """View board details."""

    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer[Any]):
        name = serializers.CharField()

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


class PostsApi(APIView):
    """Manage posts."""

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField(required=True)
        board = serializers.PrimaryKeyRelatedField(required=False, queryset=Board.objects.all())

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description="post was successfully created"),
            400: openapi.Response(description="input validation failed"),
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new post.

        The user must be a board member.
        Input is considered valid when the text is at least 10 and at maximum 1000 characters long.
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_post(**serializer.validated_data, creator=request.user)

        return Response(status=status.HTTP_201_CREATED)

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer[Any]):
        text = serializers.CharField(required=False)
        board = serializers.PrimaryKeyRelatedField(required=False, queryset=Board.objects.all())
        is_creator = serializers.BooleanField(allow_null=True, default=None, required=False)

    class OutputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField()
        creator = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
            },
        )
        edited = serializers.BooleanField()

    @swagger_auto_schema(responses={200: OutputSerializer(many=True)})  # type: ignore
    def get(self, request: Request) -> Response:
        """Retrieve list of posts."""
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        posts = post_list(**filters_serializer.validated_data, user=request.user)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=posts,
            request=request,
            view=self,
        )


class DetailPostsApi(APIView):
    """Manage post details."""

    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField()
        creator = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
            },
        )
        edited = serializers.BooleanField()

    @swagger_auto_schema(  # type: ignore
        responses={
            200: OutputSerializer(),
            404: openapi.Response(description="post does not exist"),
        }
    )
    def get(self, request: Request, post_id: int) -> Response:
        """Retrieve post details."""
        post = post_get(post_id=post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = self.OutputSerializer(post).data

        return Response(data=data, status=status.HTTP_200_OK)

    class InputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField(required=True)

    @swagger_auto_schema(  # type: ignore
        responses={
            200: openapi.Response(description="post was updated"),
            400: openapi.Response(description="validation failed"),
            403: openapi.Response(description="user is not the post creator"),
            404: openapi.Response(description="post does not exist"),
        }
    )
    def patch(self, request: Request, post_id: int) -> Response:
        """Update post."""
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = post_get(post_id=post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        update_post(post=post, data=serializer.validated_data, user=request.user)

        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(  # type: ignore
        responses={
            204: openapi.Response(description="post was deleted"),
            403: openapi.Response(description="user is not the post creator"),
            404: openapi.Response(description="post does not exist"),
        }
    )
    def delete(self, request: Request, post_id: int) -> Response:
        """Delete post."""
        post = post_get(post_id=post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        delete_post(post=post, user=request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsApi(APIView):
    """Manage comments."""

    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField(required=True)
        post = serializers.PrimaryKeyRelatedField(required=True, queryset=Post.objects.all())
        # Mypy errors are ignored here because base class Field also has a field called parent
        parent = serializers.PrimaryKeyRelatedField(required=False, queryset=Comment.objects.all())  # type:ignore

    @swagger_auto_schema(  # type: ignore
        request_body=InputSerializer,
        responses={
            201: openapi.Response(description="comment was successfully created"),
            400: openapi.Response(description="input validation failed"),
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new comment.

        The user must be a board member.
        Input is considered valid when the comment is at least 1 and at maximum 1000 characters long.
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_comment(**serializer.validated_data, creator=request.user)

        return Response(status=status.HTTP_201_CREATED)

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer[Any]):
        text = serializers.CharField(required=False)
        post = serializers.PrimaryKeyRelatedField(required=False, queryset=Post.objects.all())
        # Mypy errors are ignored here because base class Field also has a field called parent
        parent = serializers.PrimaryKeyRelatedField(required=False, queryset=Comment.objects.all())  # type:ignore

    class OutputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField()
        creator = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
            },
        )
        parent_id = serializers.IntegerField()

    @swagger_auto_schema(  # type: ignore
        responses={200: OutputSerializer(many=True)},
        query_serializer=FilterSerializer(),
    )
    def get(self, request: Request) -> Response:
        """Retrieve list of comments."""
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        comments = comment_list(**filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=comments,
            request=request,
            view=self,
        )


class DetailCommentsApi(APIView):
    """Manage comment details."""

    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer[Any]):
        text = serializers.CharField()
        creator = inline_serializer(
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
            },
        )
        parent_id = serializers.IntegerField()

    @swagger_auto_schema(  # type: ignore
        responses={
            200: OutputSerializer(),
            404: openapi.Response(description="comment does not exist"),
        }
    )
    def get(self, request: Request, comment_id: int) -> Response:
        """Retrieve comment details."""
        comment = comment_get(comment_id=comment_id)
        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = self.OutputSerializer(comment).data

        return Response(data=data, status=status.HTTP_200_OK)
