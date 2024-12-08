from django.test import TestCase
from tutorials.models import User,StudentRequest
from django.core.exceptions import ValidationError

class StudentRequestTestCase(TestCase):

    def setUp(self):
        # Set up a test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create a valid StudentRequest instance
        self.request = StudentRequest.objects.create(
            name="John Doe",
            username=self.user,
            request_type='profile_update',
            description='Request to update my profile picture.',
            status='pending',
            priority='low'
        )

    def test_valid_student_request(self):
        """Test that a valid StudentRequest instance passes validation."""
        try:
            self.request.full_clean()
        except ValidationError:
            self.fail("Valid StudentRequest instance should not raise ValidationError.")

    def test_invalid_request_type(self):
        """Test that an invalid request_type raises ValidationError."""
        self.request.request_type = 'invalid_request_type'
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_invalid_priority(self):
        """Test that an invalid priority raises ValidationError."""
        self.request.priority = 'urgent'
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_status_default_value(self):
        """Test that the default value for status is 'pending'."""
        new_request = StudentRequest(
            name="Jane Doe",
            username=self.user,
            request_type='password_reset',
            description='Forgot my password.',
            priority='medium'
        )
        new_request.full_clean()  # Should not raise errors
        self.assertEqual(new_request.status, 'pending')

    def test_invalid_status(self):
        """Test that an invalid status raises ValidationError."""
        self.request.status = 'not_valid_status'
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_max_length_name(self):
        """Test that exceeding max_length for name raises ValidationError."""
        self.request.name = 'a' * 256  # Exceeds max_length of 255
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_empty_description(self):
        """Test that an empty description raises ValidationError."""
        self.request.description = ''
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_default_priority_value(self):
        """Test that the default value for priority is 'low'."""
        new_request = StudentRequest(
            name="Alice Smith",
            username=self.user,
            request_type='course_enrollment',
            description='Enroll in course XYZ.'
        )
        new_request.full_clean()  # Should not raise errors
        self.assertEqual(new_request.priority, 'low')
