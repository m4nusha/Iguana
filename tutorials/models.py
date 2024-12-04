from django.core.validators import RegexValidator, MinValueValidator
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
    ]
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')

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

    term = models.CharField(max_length=10, choices=TERM_CHOICES, default=TERM1)
    student = models.ForeignKey(User, related_name='student_bookings', on_delete=models.CASCADE)
    tutor = models.ForeignKey(User, related_name='tutor_bookings', on_delete=models.CASCADE)


    class Meta:
        ordering = ['term', 'student', 'tutor']
        unique_together = ['term', 'student', 'tutor']
        

    def clean(self):
        if not self.student_id or not self.tutor_id:
            raise ValidationError("Both student and tutor must be assigned.")
        if self.student_id == self.tutor_id:
            raise ValidationError("A student cannot book themselves as a tutor.")
        if not User.objects.filter(id=self.student_id).exists():
            raise ValidationError(f"Student with ID {self.student_id} does not exist.")
        if not User.objects.filter(id=self.tutor_id).exists():
            raise ValidationError(f"Tutor with ID {self.tutor_id} does not exist.")
        if Booking.objects.filter(term=self.term, student_id=self.student_id, tutor_id=self.tutor_id).exists():
            raise ValidationError('A booking with the same details already exists.')

    def __str__(self):
        """return a readable string representation of booking"""
        return f'{self.term} | Student: {self.student.full_name} | Tutor: {self.tutor.full_name}'
    

class Session(models.Model):
    """Model to represent individual sessions within a booking."""
    TYPE_FORTNIGHT = 'Fortnight'
    TYPE_WEEKLY = 'Weekly'
    TYPE_BIWEEKLY = 'Bi-Weekly'

    LESSON_TYPE_CHOICES = [
        (TYPE_FORTNIGHT, 'Fortnight'),
        (TYPE_WEEKLY, 'Weekly'),
        (TYPE_BIWEEKLY, 'Bi-Weekly'),
    ]

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
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES, default='Weekly')
    venue = models.CharField(max_length=20, choices=VENUE_CHOICES, default='Bush House')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
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
        return f"Session on {self.session_date} at {self.session_time} for {self.booking.term} | Student: {self.booking.student.username} | Tutor: {self.booking.tutor.username}"


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
        super().save(*args, **kwargs)




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
    subject = models.CharField(
        max_length=100,
        choices=SUBJECT_CHOICES,
        default='Python',
    )   
    

    def save(self, *args, **kwargs):
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.username.username})"

    def description(self):
        # Provides a user-readable description excluding email
        subject_info = f"teaches ({self.get_subject_display()})" if self.get_subject_display() else "has no subject assigned"
        return f"{self.name} ({self.username.username}) {subject_info}."