from typing import TYPE_CHECKING

from django.conf import settings
from django.core.mail import send_mail

if TYPE_CHECKING:
    from boards_of_django.authentication.models import ConfirmationOTP, User

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.base")

app = Celery("boards_of_django")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task
def task_send_confirmation_email(user: "User", confirmation_otp: "ConfirmationOTP") -> str:
    """
    Send a confirmation email after user registers.

    Parameters
    ----------
    user : User who registered.
    confirmation_otp : One-time password that can be used to confirm registration.

    Returns
    -------
    "Done" message when success. Otherwise, it fails silently.

    """
    mail_subject = "Confirm registration"
    message = (
        "Hey! You have just registered in Boards of Django. Use this code to confirm your registration: "
        f"{confirmation_otp.otp}"
    )
    to_email = user.email
    send_mail(
        subject=mail_subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=True,
    )
    return "Done"
