from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from tutorials.models import Student

class StudentTestCase(TestCase):
    def setUp(self):
            name = "Doe, J."
            username = "janedoe"
            email = "janeDoe@gmail.com"
            allocated = True
            self.student = Student(name=name, username = username, email = email, allocated = allocated)

    #blank & too long testing
    def test_blank_name_is_invalid(self):
        self.student.name = ""
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    def test_overlong_name_is_invalid(self):
        self.student.name = 'x'*256
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    def test_blank_username_is_invalid(self):
        self.student.username = ""
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    def test_overlong_username_is_invalid(self):
        self.student.username = 'x'*256
        with self.assertRaises(ValidationError):
            self.student.full_clean()

        # Test: Username uniqueness
    def test_student_username_must_be_unique(self):
        self.student.save()
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                name="Jane Doe",
                username="janedoe",  # Duplicate username
                email="jane.doe2@gmail.com",
                allocated=False
            )

    def test_blank_email_is_invalid(self):
        self.student.email = ""
        with self.assertRaises(ValidationError):
            self.student.full_clean()  # Validates the model instance

    def test_overlong_email_is_invalid(self):
        self.student.email = "x" * 255 + "@example.com"  # Exceeds the max_length of 254 (default length)
        with self.assertRaises(ValidationError):
            self.student.full_clean()  # Validates the model instance

            # Test: Email uniqueness
    def test_student_email_must_be_unique(self):
        self.student.save()
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                name="Jane Doe",
                username="janedoe2",
                email="janedoe@gmail.com",  # Duplicate email
                allocated=False
            )

        # Test: Allocated default value is False
    def test_default_allocated_is_false(self):
        student = Student(
            name="Jane Doe",
            username="janedoe",
            email="jane.doe@gmail.com"
        )
        student.full_clean()
        student.save()
        self.assertFalse(student.allocated)

        # Test: Allocated cannot take non-boolean value
    def test_non_boolean_allocated_is_invalid(self):
        self.student.allocated = "not a boolean"
        with self.assertRaises(ValidationError):
            self.student.full_clean()

        # Test: String representation (__str__)
    def test_string_representation(self):
        expected_str = f"{self.student.name} ({self.student.username}) ({self.student.email}), Allocated? {'Yes' if self.student.allocated else 'No'}"
        self.assertEqual(str(self.student), expected_str)

        # Test: Description method
    def test_description(self):
        allocation_status = 'allocated' if self.student.allocated else 'not allocated'
        expected_description = f"{self.student.name} ({self.student.username}) is {allocation_status}."
        self.assertEqual(self.student.description(), expected_description)

    def test_valid_student_instance_can_be_saved(self):
        self.student.full_clean()  # Validate the instance
        self.student.save()
        self.assertEqual(Student.objects.count(), 1)

