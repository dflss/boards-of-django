from django.urls import path

from boards.apis import BoardsApi, DetailBoardsApi

urlpatterns = [
    path("", BoardsApi.as_view(), name="boards"),
    path("", BoardsApi.as_view(), name="boards"),
    path("<int:board_id>/", DetailBoardsApi.as_view(), name="board_detail"),
]
