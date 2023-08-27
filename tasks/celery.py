import os
from typing import TYPE_CHECKING

from celery import Celery
from django.core.mail import send_mail

from config.django import settings

if TYPE_CHECKING:
    from authentication.models import ConfirmationOTP, User

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.settings")
app = Celery("boards_of_django")
app.config_from_object("config.django:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


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
