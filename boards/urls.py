from django.urls import path

from boards.apis import AddAdminsBoardsApi, BoardsApi, DetailBoardsApi

urlpatterns = [
    path("", BoardsApi.as_view(), name="boards"),
    path("<int:board_id>/", DetailBoardsApi.as_view(), name="board_detail"),
    path("<int:board_id>/join/", DetailBoardsApi.join, name="board_detail_join"),
    path("<int:board_id>/add-admin/", AddAdminsBoardsApi.as_view(), name="board-detail-add-admin"),
]
