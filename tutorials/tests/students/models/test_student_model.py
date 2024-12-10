from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from django.test import TestCase
from tutorials.models import Student, User

class StudentTestCase(TestCase):
    def setUp(self):
        # Create a user for the ForeignKey field
        self.user = User.objects.create_user(
            username="@janedoe",
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            user_type="student",
        )
        # Use the Student instance created by the User.save method
        self.student = Student.objects.get(username=self.user)

    # Test: Valid student instance can be saved
    def test_valid_student_instance_can_be_saved(self):
        self.student.full_clean()
        self.student.save()
        self.assertEqual(Student.objects.count(), 1)

    # Test: Blank name is invalid
    def test_blank_name_is_invalid(self):
        self.student.name = ""
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Overlong name is invalid
    def test_overlong_name_is_invalid(self):
        self.student.name = "x" * 256
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Username must be a valid User
    def test_username_must_be_valid_user(self):
        self.student.username = None
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Reuse unique username with different email
    def test_student_can_reference_same_username(self):
        self.student.save()
        new_email = "unique.email@example.com"
        another_student = Student(
            name="John Doe",
            username=self.user,  # Same user reference
            email=new_email,  # Different email
            allocated=False,
        )
        another_student.full_clean()
        another_student.save()
        self.assertEqual(Student.objects.count(), 2)
        self.assertEqual(Student.objects.last().email, new_email)


    # Test: Blank email is invalid
    def test_blank_email_is_invalid(self):
        self.student.email = ""
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Overlong email is invalid
    def test_overlong_email_is_invalid(self):
        self.student.email = "x" * 255 + "@example.com"
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    def test_student_email_must_be_unique(self):
        # Save the initial student instance
        self.student.save()

        # Create a new User for the second Student instance
        new_user = User.objects.create_user(
            username="@johnsmith", email="john.smith@example.com"
        )

        # Attempt to create a Student with a duplicate email and assert IntegrityError is raised
        with self.assertRaises(IntegrityError):
            with transaction.atomic():  # Ensure atomicity to prevent breaking the transaction
                Student.objects.create(
                    name="John Smith",
                    username=new_user,
                    email="jane.doe@example.com",  # Duplicate email
                    allocated=False,
                )

    # Test: Default allocated value is False
    def test_default_allocated_is_false(self):
        student = Student(
            name="John Smith",
            username=self.user,
            email="john.smith@example.com"
        )
        student.full_clean()
        student.save()
        self.assertFalse(student.allocated)

    # Test: Allocated must be a boolean
    def test_non_boolean_allocated_is_invalid(self):
        self.student.allocated = "not a boolean"
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Valid payment status
    def test_valid_payment_status(self):
        valid_statuses = ["Pending", "Successful"]
        for status in valid_statuses:
            self.student.payment = status
            self.student.full_clean()
            self.student.save()
            self.assertEqual(self.student.payment, status)

    # Test: Invalid payment status
    def test_invalid_payment_status(self):
        self.student.payment = "InvalidStatus"
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Default payment status is Pending
    def test_default_payment_status(self):
        student_no_payment = Student(
            name="Jane Doe",
            username=self.user,
            email="jane.doe@gmail.com",
            allocated=False
        )
        student_no_payment.full_clean()
        student_no_payment.save()
        self.assertEqual(student_no_payment.payment, "Pending")

    # Test: Email normalization
    def test_email_normalization(self):
        self.student.email = "Jane.DOE@EXAMPLE.COM"
        self.student.save()
        self.assertEqual(self.student.email, "jane.doe@example.com")

    # Test: String representation
    def test_string_representation(self):
        expected_str = f"{self.student.name} ({self.student.username.username}) ({self.student.email}), Allocated? {'Yes' if self.student.allocated else 'No'}, Payment Status: {self.student.payment}"
        self.assertEqual(str(self.student), expected_str)

    # Test: Description method
    def test_description(self):
        allocation_status = "allocated" if self.student.allocated else "not allocated"
        expected_description = f"{self.student.name} ({self.student.username.username}) is {allocation_status} and has payment status {self.student.payment}."
        self.assertEqual(self.student.description(), expected_description)
