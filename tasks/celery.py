from typing import TYPE_CHECKING

from celery import Celery
from django.core.mail import send_mail

from boards_of_django import settings

if TYPE_CHECKING:
    from authentication.models import ConfirmationOTP, User

app = Celery("boards_of_django")
app.config_from_object("django.conf:settings", namespace="CELERY")
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
        f"Hey! You have just registered in Boards of Django. Use this code to confirm your registration: "
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
