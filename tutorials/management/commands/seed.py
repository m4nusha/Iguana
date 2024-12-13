from datetime import datetime, timedelta
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
    SESSION_COUNT = 200
    STUDENT_REQUEST_COUNT = 50
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data.'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        #Tala says add the functions in handle here
        

    def handle(self, *args, **options):
        """Main entry point for the seeding process."""
        self.create_users()
        self.debug_student_and_tutor_counts()  # Debugging step
        self.generate_random_bookings()
        self.generate_random_sessions()
        self.generate_random_student_requests()

    def create_users(self):
        """Creates users from fixtures and generates additional random users."""
        self.create_admin_user()
        self.generate_user_fixtures()
        self.generate_random_users()    #ERROR
    

    def create_admin_user(self):
        """Ensures John Doe is the only admin."""
        admin_data = next((user for user in user_fixtures if user['user_type'] == 'Admin'), None)
        if admin_data:
            self.try_create_user(admin_data)

    def generate_user_fixtures(self):
        """Creates predefined users from fixtures, excluding the admin."""
        for data in user_fixtures:
            if data['user_type'] != 'Admin':  # Skip admin as it's handled separately
                self.try_create_user(data)

    def generate_random_users(self):
        """Generates random users until USER_COUNT is met."""
        user_count = User.objects.exclude(user_type='admin').count()
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
            user_count = User.objects.exclude(user_type='admin').count()

        print("Users seeding complete.")

    def try_create_user(self, data):
        """Attempts to create a user and logs errors."""
        try:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'password': self.DEFAULT_PASSWORD,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'user_type': data['user_type'].lower(),
                }
            )
            if created:
                if data['user_type'].lower() == 'student':
                    student, created = Student.objects.get_or_create(
                        username=user,
                        defaults={
                            'name': f"{data['first_name']} {data['last_name']}",
                            'email': data['email'],
                            'allocated': random.choice([True, False]),
                            'payment': random.choice(['Successful', 'Pending']),
                            }
                        )
                    if not created:
                        # Update existing student with random payment if already created
                        student.payment = random.choice(['Successful', 'Pending'])
                        student.allocated = random.choice([True, False])
                        student.save()

                elif data['user_type'].lower() == 'tutor':
                    tutor, created = Tutor.objects.get_or_create(
                        username=user,
                        defaults={
                            'name': f"{data['first_name']} {data['last_name']}",
                            'email': data['email'],
                            'rate': random.choice([10.0, 20.0, 30.0, 40.0, 50.0]),
                        }
                    )
                    # Assign dynamic rate and subjects even if tutor already exists
                    if not created:
                        tutor.rate = random.choice([10.0, 20.0, 30.0, 40.0, 50.0])
                        tutor.save()

                elif data['user_type'].lower() == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.set_password(self.DEFAULT_PASSWORD)
                    user.save()
        except Exception as e:
            print(f"Error creating user {data['username']}: {e}")

    def debug_student_and_tutor_counts(self):
        """Logs counts of students and tutors."""
        student_count = Student.objects.count()
        tutor_count = Tutor.objects.count()
        print(f"Students in DB: {student_count}")
        print(f"Tutors in DB: {tutor_count}")

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
        """Generates exactly one session per booking."""
        bookings = Booking.objects.all()
        venues = ['Bush House', 'Waterloo Campus']
        
        if not bookings.exists():
            print("No bookings available to create sessions.")
            return

        for booking in bookings:
            session_date = self.faker.date_between(start_date="today", end_date="+90d")
            session_time = self.faker.time(pattern='%H:%M:%S', end_datetime=None)
            duration = timedelta(hours=random.randint(1, 4))
            venue = random.choice(venues)
            payment_status = random.choice(['Pending', 'Successful'])

            try:
                # Ensure only one session is created per booking
                if not Session.objects.filter(booking=booking).exists():
                    Session.objects.create(
                        booking=booking,
                        session_date=session_date,
                        session_time=session_time,
                        duration=duration,
                        venue=venue,
                        payment_status=payment_status,
                    )
            except Exception as e:
                print(f"Error creating session for booking {booking.id}: {e}")

        print("Sessions seeding complete.")


    def generate_random_student_requests(self):
        """Generates random student requests."""
        students = Student.objects.all()

        if not students.exists():
            print("No students available to create student requests.")
            return

        for _ in range(self.STUDENT_REQUEST_COUNT):
            student = random.choice(students)
            request_data = {
                'Profile Update': [
                    "The user has requested an update to their profile information.",
                    "The student has raised a request to modify their contact details.",
                ],
                'Password Reset': [
                    "The student has requested a reset of their account password.",
                    "The user has reported issues accessing their account due to a forgotten password.",
                ],
                'Course Enrollment': [
                    "The student has submitted a request to enroll in a new course.",
                    "A request has been raised for enrollment in advanced programming classes.",
                ],
                'Tutor Assignment': [
                    "The student has requested a new tutor assignment.",
                    "A request has been made to change the assigned tutor.",
                ],
                'Session Scheduling': [
                    "The student is facing issues with scheduling their sessions.",
                    "A request has been made to reschedule the upcoming tutoring session.",
                ],
                'Payment Issue': [
                    "The user has reported a problem with the payment process.",
                    "A request has been raised to resolve pending payment issues.",
                ],
                'Technical Support': [
                    "The student has reported a technical issue with the learning platform.",
                    "A request has been submitted for assistance with platform access.",
                ],
                'Feedback/Complaint': [
                    "The user has provided feedback about their recent session.",
                    "A complaint has been raised regarding the tutor's availability.",
                ],
                'Custom Request': [
                    "The student has submitted a unique request not covered by standard categories.",
                    "A custom request has been made for additional learning resources.",
                ],
            }
            request_type = random.choice(list(request_data.keys()))
            description = random.choice(request_data[request_type])
            status = random.choice(['Pending', 'In Progress', 'Resolved'])
            priority = random.choice(['Low', 'Medium', 'High'])
            created_at = self.faker.date_between(start_date='-30d', end_date='today')

            try:
                StudentRequest.objects.create(
                    name=student.name,
                    username=student.username,
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