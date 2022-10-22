from django.urls import path

from boards.apis import (
    AddAdminsBoardsApi,
    BoardsApi,
    CommentsApi,
    DetailBoardsApi,
    DetailCommentsApi,
    DetailPostsApi,
    JoinBoardsApi,
    PostsApi,
)

urlpatterns = [
    path("boards/", BoardsApi.as_view(), name="boards"),
    path("boards/<int:board_id>/", DetailBoardsApi.as_view(), name="board-detail"),
    path("boards/<int:board_id>/join/", JoinBoardsApi.as_view(), name="board-detail-join"),
    path("boards/<int:board_id>/add-admin/", AddAdminsBoardsApi.as_view(), name="board-detail-add-admin"),
    path("posts/", PostsApi.as_view(), name="posts"),
    path("posts/<int:post_id>/", DetailPostsApi.as_view(), name="post-detail"),
    path("comments/", CommentsApi.as_view(), name="comments"),
    path("comments/<int:comment_id>/", DetailCommentsApi.as_view(), name="comment-detail"),
]
