from typing import Any, Dict, List, Tuple

from common.types import DjangoModelType


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
    fields : Fields to be updated
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
        instance.save(update_fields=fields)

    return instance, has_updated
