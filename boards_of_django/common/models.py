from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Base model class that allows to audit the timestamp when the object in database was created and modified.

    Attributes:
    ----------
    created_at : Timestamp when the object was created
    updated_at : Timestamp when the object last updated
    """

    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
