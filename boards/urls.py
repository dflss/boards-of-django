from django.urls import path

from boards.apis import AddAdminsBoardsApi, BoardsApi, DetailBoardsApi, JoinBoardsApi

urlpatterns = [
    path("", BoardsApi.as_view(), name="boards"),
    path("<int:board_id>/", DetailBoardsApi.as_view(), name="board-detail"),
    path("<int:board_id>/join/", JoinBoardsApi.as_view(), name="board-detail-join"),
    path("<int:board_id>/add-admin/", AddAdminsBoardsApi.as_view(), name="board-detail-add-admin"),
]
