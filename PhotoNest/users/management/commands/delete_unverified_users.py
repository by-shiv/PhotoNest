from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser


class Command(BaseCommand):

    help = "Delete unverified users older than 12 hours"

    def handle(self, *args, **kwargs):

        cutoff_time = (
            timezone.now() -
            timedelta(hours=12)
        )

        deleted_count, _ = CustomUser.objects.filter(
            email_verified=False,
            date_joined__lt=cutoff_time
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_count} unverified users."
            )
        )