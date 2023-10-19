from typing import Any, Dict, List, Tuple

from django.db.models import DateTimeField

from boards_of_django.common.types import DjangoModelType


def model_update(
    *, instance: DjangoModelType, fields: List[str], data: Dict[str, Any]
) -> Tuple[DjangoModelType, bool]:
    """
    Update model.

    This code is a generic update service meant to be reused in local update services and was taken from
    Django-Styleguide: https://github.com/HackSoftware/Django-Styleguide-Example

    Parameters
    ----------
    instance : Instance to be updated
    fields : Fields to be updated. Note that fields with auto_add=True are automatically updated
    data : Dictionary with fields to be updated and their new values

    Returns
    -------
    Tuple with the following elements:
        1. The instance we updated
        2. A boolean value representing whether we performed an update or not.
    """
    has_updated = False

    for field in fields:
        # Skip if a field is not present in the actual data
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            has_updated = True
            setattr(instance, field, data[field])

    # Perform an update only if any of the fields was actually changed
    if has_updated:
        instance.full_clean()
        # Update only the fields that are meant to be updated.
        # Django docs reference:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#specifying-which-fields-to-save
        # As per Django docs, the date/time fields with auto_now=True will not be updated unless they are included in
        # the update_fields, so we need to include them.
        for model_field in instance._meta.fields:
            # The type stubs for DateField and TimeField are missing the attributes "auto_now_add" and "auto_now".
            # This also effects DateTimeField, which inherits from DateField.
            # Open issue: https://github.com/typeddjango/django-stubs/issues/479
            if type(model_field) is DateTimeField and model_field.auto_now is True:
                fields.append(model_field.name)
        instance.save(update_fields=fields)

    return instance, has_updated
