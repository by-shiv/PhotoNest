from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):

    help = "Delete all users except main account"

    def handle(self, *args, **kwargs):

        KEEP_EMAIL = "shivanshsingh.0019@gmail.com"

        deleted_count = 0

        for user in CustomUser.objects.all():

            if user.email.lower() != KEEP_EMAIL.lower():

                print(
                    f"Deleting: {user.username} | {user.email}"
                )

                user.delete()

                deleted_count += 1

        print()
        print(f"Deleted Users: {deleted_count}")
        print()

        print("Remaining Users:")

        for user in CustomUser.objects.all():

            print(
                f"{user.username} | {user.email}"
            )