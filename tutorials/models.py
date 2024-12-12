from decimal import Decimal
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from libgravatar import Gravatar
from django.db import models
from datetime import datetime, timedelta, date, time



class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    USER_TYPES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('not specified', 'Not Specified'),
        ('admin', 'Admin')
    ]
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='student')

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']
    @property
    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'
    
    @property
    def is_student(self):
        return hasattr(self, 'students')

    @property
    def is_tutor(self):
        return hasattr(self, 'tutors')

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the User is being created

        if self.username == "@johndoe":
            self.user_type = 'admin'

        super().save(*args, **kwargs)  # Call the parent save method
        
        # Ensure a Student instance is created if the user_type is 'student'
        if self.user_type == 'student' and not Student.objects.filter(username=self).exists():
            Student.objects.create(username=self, name=self.full_name, email=self.email)
        
        # Ensure a Tutor instance is created if the user_type is 'tutor'
        if self.user_type == 'tutor' and not Tutor.objects.filter(username=self).exists():
            Tutor.objects.create(username=self, name=self.full_name, email=self.email)

        # If switching user_type from 'tutor' to 'student', delete related Tutor
        if not is_new and self.user_type == 'student':
            Tutor.objects.filter(username=self).delete()

        # If switching user_type from 'student' to 'tutor', delete related Student
        if not is_new and self.user_type == 'tutor':
            Student.objects.filter(username=self).delete()


class Student(models.Model):
    PENDING = 'Pending'
    SUCCESSFUL = 'Successful'

    PAYMENT_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESSFUL, 'Successful'),
    ]

    name = models.CharField(max_length=255)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')  # ForeignKey
    email = models.EmailField(unique=True)
    allocated = models.BooleanField(default=False)
    payment = models.CharField( 
        max_length=10,
        choices=PAYMENT_CHOICES,
        default=PENDING,
    )

    def save(self, *args, **kwargs):
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        # Show Yes/No for the boolean field
        return f"{self.name} ({self.username.username}) ({self.email}), Allocated? {'Yes' if self.allocated else 'No'}, Payment Status: {self.payment}"

    def description(self):
        # Provide a short, user-readable description excluding email
        allocation_status = 'allocated' if self.allocated else 'not allocated'
        return f"{self.name} ({self.username.username}) is {allocation_status} and has payment status {self.payment}."


class StudentRequest(models.Model):
    # Types of requests
    REQUEST_TYPE_CHOICES = [
        ('profile_update', 'Profile Update'),
        ('password_reset', 'Password Reset'),
        ('course_enrollment', 'Course Enrollment'),
        ('tutor_assignment', 'Tutor Assignment'),
        ('session_schedule', 'Session Scheduling'),
        ('payment_issue', 'Payment Issue'),
        ('technical_support', 'Technical Support'),
        ('feedback_complaint', 'Feedback/Complaint'),
        ('custom_request', 'Custom Request'),
    ]

    # Priority levels
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    name = models.CharField(max_length=255)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_requests')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPE_CHOICES)
    description = models.TextField()  # Detailed description of the request
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')],
        default='pending',
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')

    # Automatically adds the current timestamp when the record is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username.username} - {self.get_request_type_display()}"

    def show_details(self):
        return (
            f"Student: {self.username.username}\n"
            f"Request Type: {self.get_request_type_display()}\n"
            f"Description: {self.description}\n"
            f"Status: {self.get_status_display()}\n"
            f"Priority: {self.get_priority_display()}\n"
            f"Created At: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

class Subject(models.Model):
    name = models.CharField(max_length=100 ,unique = True)

    def __str__(self):
        return self.name

class Tutor(models.Model):
    SUBJECT_CHOICES = [
        ('Python', 'Python'),
        ('Java', 'Java'),
        ('Javascript', 'Javascript'),
        ('React', 'React'),
        ('Ruby', 'Ruby'),
        ('Go', 'Go'),
        ('HTML/CSS', 'HTML/CSS'),
        ('C', 'C'),
        ('Scala', 'Scala'),
    ]
    name = models.CharField(max_length=255)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutors')
    email = models.EmailField(unique=True)
    subjects = models.ManyToManyField(Subject, related_name='tutors') #dynamic subjects
    rate = models.DecimalField(max_digits=6, decimal_places=2, default=10.00, validators=[MinValueValidator(Decimal('0.01'))],)  
    

    def save(self, *args, **kwargs):
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
        if not self.subjects.exists():
            python_subject, created = Subject.objects.get_or_create(name="Python")
            self.subjects.add(python_subject)

    def __str__(self):
        return f"{self.name} ({self.username.username})"

    def description(self):
    # Provides a user-readable description with all assigned subjects
        subject_info = ", ".join(subject.name for subject in self.subjects.all()) if self.subjects.exists() else "has no subject assigned"
        return f"{self.name} ({self.username.username}) teaches {subject_info}."



class Booking(models.Model):
    """Model to represent a booking between a student and a tutor."""
    TERM1 = 'Term1'
    TERM2 = 'Term2'
    TERM3 = 'Term3'

    TERM_CHOICES = [
        (TERM1, 'Term 1'),
        (TERM2, 'Term 2'),
        (TERM3, 'Term 3'),
    ]

    TYPE_FORTNIGHT = 'Fortnight'
    TYPE_WEEKLY = 'Weekly'
    TYPE_BIWEEKLY = 'Bi-Weekly'

    LESSON_TYPE_CHOICES = [
        (TYPE_FORTNIGHT, 'Fortnight'),
        (TYPE_WEEKLY, 'Weekly'),
        (TYPE_BIWEEKLY, 'Bi-Weekly'),
    ]

    term = models.CharField(max_length=10, choices=TERM_CHOICES, default=TERM1)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES, default='Weekly')
    student = models.ForeignKey(Student, related_name='student_bookings', on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, related_name='tutor_bookings', on_delete=models.CASCADE)

    class Meta:
        ordering = ['term', 'lesson_type', 'student', 'tutor']
        unique_together = ['term', 'lesson_type', 'student', 'tutor']

    def clean(self):        
        if not self.student_id or not self.tutor_id:
            raise ValidationError("Both student and tutor must be assigned.")
        if not Student.objects.filter(id=self.student_id).exists():
            raise ValidationError(f"Student with ID {self.student_id} does not exist.")
        if not Tutor.objects.filter(id=self.tutor_id).exists():
            raise ValidationError(f"Tutor with ID {self.tutor_id} does not exist.")
        if self.student_id == self.tutor_id:
            raise ValidationError("A student cannot book themselves as a tutor.")
        if Booking.objects.filter(term=self.term,lesson_type=self.lesson_type, student_id=self.student_id, tutor_id=self.tutor_id).exists():
            raise ValidationError('A booking with the same details already exists.')

    def __str__(self):
        """return a readable string representation of booking"""
        return f'{self.term} | {self.lesson_type} | Student: {self.student.name} | Tutor: {self.tutor.name}'
    

class Session(models.Model):
    """Model to represent individual sessions within a booking."""
    
    PAYMENT_PENDING = 'Pending'
    PAYMENT_SUCCESSFUL = 'Successful'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_SUCCESSFUL, 'Successful'),
    ]

    VENUE_BUSH_HOUSE = 'Bush House'
    VENUE_WATERLOO = 'Waterloo Campus'

    VENUE_CHOICES = [
        (VENUE_BUSH_HOUSE, 'Bush House'),
        (VENUE_WATERLOO, 'Waterloo Campus'),
    ]

    booking = models.ForeignKey(Booking, related_name='sessions', on_delete=models.CASCADE)
    session_date = models.DateField(default=date(2025, 1, 1))  # Use date object
    session_time = models.TimeField(default=time(0, 0))  # Use time object
    duration = models.DurationField(help_text='Format: [hours]:[minutes]', default=timedelta(hours=1))
    venue = models.CharField(max_length=20, choices=VENUE_CHOICES, default='Bush House')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['booking', 'session_date', 'session_time'],
                name='unique_booking_session_datetime'
            )
        ]

    def __str__(self):
        """return a readable string representation of the session"""
        return f"Session on {self.session_date} at {self.session_time} for {self.booking.term} | Student: {self.booking.student.username.username} | Tutor: {self.booking.tutor.username.username}"


    def clean(self):
        super().clean()
        if not self.booking:
            raise ValidationError("A valid booking is required to create a session.")
        if self.session_date < date.today():
            raise ValidationError("Session date cannot be in the past.")

        start_datetime = datetime.combine(self.session_date, self.session_time)
        end_datetime = start_datetime + self.duration
        overlapping_sessions = Session.objects.filter(
            booking=self.booking,
            session_date=self.session_date,
        ).exclude(pk=self.pk)

        for session in overlapping_sessions:
            session_start = datetime.combine(session.session_date, session.session_time)
            session_end = session_start + session.duration
            if max(start_datetime, session_start) < min(end_datetime, session_end):
                raise ValidationError("This session overlaps with another session for the same booking.")

        if self.duration.total_seconds() <= 0:
            raise ValidationError({"duration": "Session duration must be greater than zero."})
  
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.booking:
            return super().save(*args, **kwargs)

        super().save(*args, **kwargs)
    

    def calculate_total_amount(self):
        tutor = self.booking.tutor # UserInstance
        tutor_instance = self.booking.tutor
        tutor_rate=tutor_instance.rate

        term_weeks = {
            'Term1': Decimal(14),
            'Term2': Decimal(11),
            'Term3': Decimal(11),
        }
        lesson_type_multiplier = {
            'Weekly': Decimal(1),
            'Bi-Weekly': Decimal(2),
            'Fortnight': Decimal(0.5),
        }
        # Get the term, lesson type, and duration in hours (in Decimal)
        term = self.booking.term
        lesson_type = self.booking.lesson_type
        duration_hours = Decimal(self.duration.total_seconds() / 3600) if self.duration else Decimal(1)
        weeks = term_weeks.get(term, 0)
        multiplier = lesson_type_multiplier.get(lesson_type, Decimal(1))

        return tutor_rate * duration_hours * weeks * multiplier
    
    @property
    def total_amount(self):
        return self.calculate_total_amount()