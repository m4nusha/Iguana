from django.core.management.base import BaseCommand
from tutorials.models import User, Student, Tutor, Booking, Session, StudentRequest, Subject


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseed the database by deleting all sample data.'

    def handle(self, *args, **options):
        """Unseed the database."""
        self.stdout.write("Starting database unseeding...")

        try:
            # Delete data from dependent models first to avoid integrity errors
            Session.objects.all().delete()
            self.stdout.write("Deleted all Session data.")

            Booking.objects.all().delete()
            self.stdout.write("Deleted all Booking data.")

            StudentRequest.objects.all().delete()
            self.stdout.write("Deleted all StudentRequest data.")

            Tutor.objects.all().delete()
            self.stdout.write("Deleted all Tutor data.")

            Student.objects.all().delete()
            self.stdout.write("Deleted all Student data.")

            Subject.objects.all().delete()
            self.stdout.write("Deleted all Subject data.")

            # Delete non-staff users
            User.objects.filter(is_staff=False).delete()
            self.stdout.write("Deleted all non-staff User data.")

            self.stdout.write(self.style.SUCCESS("Database unseeding complete."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unseeding failed: {e}"))

        

        

