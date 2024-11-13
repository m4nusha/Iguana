from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.db import models

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
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']
    @property
    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)

class Student(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    allocated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        # Show Yes/No for the boolean field
        return f"{self.name} ({self.username}) ({self.email}), Allocated? {'Yes' if self.allocated else 'No'}"

    def description(self):
        # Provide a short, user-readable description excluding email
        allocation_status = 'allocated' if self.allocated else 'not allocated'
        return f"{self.name} ({self.username}) is {allocation_status}."


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
        """Model options."""
        ordering = ['term', 'student', 'tutor']

    def __str__(self):
        """Return a readable string representation of the booking."""
        return f'{self.term} | Student: {self.student.full_name} | Tutor: {self.tutor.full_name}'
