from datetime import timedelta
from django.core.management.base import BaseCommand
from tutorials.models import User, Student, Tutor, Booking, Session, StudentRequest, Subject
import random
from faker import Faker

# Predefined user data for fixtures
user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'user_type': 'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'user_type': 'Tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'user_type': 'Student'},
]

class Command(BaseCommand):
    """Command to seed the database with test data."""

    USER_COUNT = 300
    BOOKING_COUNT = 200
    SESSION_COUNT = 100
    STUDENT_REQUEST_COUNT = 50
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data.'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        """Main entry point for the seeding process."""
        self.create_users()
        self.generate_random_bookings()
        self.generate_random_sessions()
        self.generate_random_student_requests()

    def create_users(self):
        """Creates users from fixtures and generates additional random users."""
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        """Creates predefined users from fixtures."""
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        """Generates random users until USER_COUNT is met."""
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = self.create_email(first_name, last_name)
            username = self.create_username(first_name, last_name)
            user_type = self.generate_random_user_type()

            user_data = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'user_type': user_type,
            }
            self.try_create_user(user_data)
            user_count = User.objects.count()

        print("Users seeding complete.")

    def try_create_user(self, data):
        """Attempts to create a user and logs errors."""
        try:
            User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'password': self.DEFAULT_PASSWORD,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'user_type': data['user_type'].lower(),
                }
            )
        except Exception as e:
            print(f"Error creating user {data['username']}: {e}")

    def generate_random_bookings(self):
        """Generates random bookings."""
        terms = ['Term 1', 'Term 2', 'Term 3']
        lesson_types = ['Fortnight', 'Weekly', 'Bi-Weekly']
        students = Student.objects.all()
        tutors = Tutor.objects.all()

        if not students.exists() or not tutors.exists():
            print("No students or tutors available to create bookings.")
            return

        for _ in range(self.BOOKING_COUNT):
            student = random.choice(students)
            tutor = random.choice(tutors)
            term = random.choice(terms)
            lesson_type = random.choice(lesson_types)

            try:
                Booking.objects.get_or_create(
                    term=term,
                    lesson_type=lesson_type,
                    student=student,
                    tutor=tutor
                )
            except Exception as e:
                print(f"Error creating booking: {e}")

        print("Bookings seeding complete.")

    def generate_random_sessions(self):
        """Generates random sessions."""
        bookings = Booking.objects.all()
        venues = ['Bush House', 'Waterloo Campus']

        if not bookings.exists():
            print("No bookings available to create sessions.")
            return

        for _ in range(self.SESSION_COUNT):
            booking = random.choice(bookings)
            session_date = self.faker.date_between(start_date="today", end_date="+90d")
            session_time = self.faker.time_object()
            duration = timedelta(hours=random.randint(1, 4))
            venue = random.choice(venues)
            payment_status = random.choice(['Pending', 'Successful'])

            try:
                Session.objects.create(
                    booking=booking,
                    session_date=session_date,
                    session_time=session_time,
                    duration=duration,
                    venue=venue,
                    payment_status=payment_status,
                )
            except Exception as e:
                print(f"Error creating session: {e}")

        print("Sessions seeding complete.")

    def generate_random_student_requests(self):
        """Generates random student requests."""
        students = Student.objects.all()

        if not students.exists():
            print("No students available to create student requests.")
            return

        for _ in range(self.STUDENT_REQUEST_COUNT):
            student = random.choice(students)
            request_type = random.choice([
                'Profile Update', 'Password Reset', 'Course Enrollment',
                'Tutor Assignment', 'Session Scheduling', 'Payment Issue',
                'Technical Support', 'Feedback/Complaint', 'Custom Request'
            ])
            description = self.faker.text(max_nb_chars=200)
            status = random.choice(['Pending', 'In Progress', 'Resolved'])
            priority = random.choice(['Low', 'Medium', 'High'])
            created_at = self.faker.date_between(start_date='-30d', end_date='today')

            try:
                StudentRequest.objects.create(
                    name=student.name,
                    username=student.username,  # Ensure this is a User instance
                    request_type=request_type,
                    description=description,
                    status=status,
                    priority=priority,
                    created_at=created_at
                )
            except Exception as e:
                print(f"Error creating student request: {e}")

        print("Student requests seeding complete.")

    def create_username(self, first_name, last_name):
        """Generates a unique username."""
        base_username = f"@{first_name.strip().lower()}{last_name.strip().lower()}"
        counter = 1
        username = base_username

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def create_email(self, first_name, last_name):
        """Generates a unique email."""
        base_email = f"{first_name.strip().lower()}.{last_name.strip().lower()}@example.org"
        counter = 1
        email = base_email

        while User.objects.filter(email=email).exists():
            email = f"{first_name.strip().lower()}.{last_name.strip().lower()}{counter}@example.org"
            counter += 1

        return email

    def generate_random_user_type(self):
        """Randomly selects a user type."""
        return random.choices(['Student', 'Tutor'], weights=[70, 30])[0]
