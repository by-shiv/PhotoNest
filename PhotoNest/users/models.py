from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    email = models.EmailField(
        unique=True
    )

    email_verified = models.BooleanField(default=False)

    otp = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    otp_created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    last_otp_sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    failed_login_attempts = models.PositiveIntegerField(
        default=0
    )

    account_locked_until = models.DateTimeField(
        null=True,
        blank=True
    )