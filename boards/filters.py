from typing import List

from django.contrib.auth import get_user_model
from django_filters import CharFilter, FilterSet, ModelMultipleChoiceFilter

from boards.models import Board

User = get_user_model()


class BoardFilter(FilterSet):
    """Filters that can be applied to Board queryset."""

    name = CharFilter(lookup_expr="icontains")
    members = ModelMultipleChoiceFilter(queryset=User.objects.all())
    admins = ModelMultipleChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Board
        fields: List[str] = []
