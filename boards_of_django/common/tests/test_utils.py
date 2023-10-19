from typing import Any

import pytest
from django.urls import reverse

from boards_of_django.common.utils import reverse_with_query_params


@pytest.mark.parametrize(
    ("query_kwargs", "expected_url_suffix"),
    [
        (
            {},
            "",
        ),
        (
            {
                "name": "test",
            },
            "?name=test",
        ),
        (
            {
                "name": "test",
                "test": 123,
            },
            "?name=test&test=123",
        ),
    ],
)
def test_reverse_with_query_params(query_kwargs: dict[str, Any] | None, expected_url_suffix: str) -> None:
    base_url = reverse("boards:boards")
    assert reverse_with_query_params("boards:boards", query_kwargs=query_kwargs) == f"{base_url}{expected_url_suffix}"
