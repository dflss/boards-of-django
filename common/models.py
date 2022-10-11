from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Define base model that can be inherited by other models.

    Attributes:
    created_at -- timestamp when the object was created
    updated_at -- timestamp when the object last updated
    """

    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
