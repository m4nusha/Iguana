from tutorials.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from tutorials.models import Student

class StudentTestCase(TestCase):
    def setUp(self):
        # Create a user for the ForeignKey field
        self.user = User.objects.create(username="janedoe")
        
        name = "Doe, J."
        username = self.user  # Reference the User object
        email = "janeDoe@gmail.com"
        allocated = True
        payment = "Pending"  
        self.student = Student(name=name, username=username, email=email, allocated=allocated, payment=payment)

    #blank & too long testing
    def test_blank_name_is_invalid(self):
        self.student.name = ""
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    def test_overlong_name_is_invalid(self):
        self.student.name = 'x'*256
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Username must be a valid User
    def test_username_must_be_valid_user(self):
        self.student.username = None  # Setting username to None
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    # Test: Username uniqueness (handled by the User model, not Student)
    def test_student_can_reference_same_username(self):
        # Create another student referencing the same username (ForeignKey)
        self.student.save()
        another_student = Student(
            name="Jane Doe",
            username=self.user,  # Same user reference
            email="jane.doe2@gmail.com",
            allocated=False
        )
        another_student.full_clean()  # Should not raise validation error
        another_student.save()
        self.assertEqual(Student.objects.count(), 2)


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
        new_user = User.objects.create(username="janedoe2", email="janedoe2@gmail.com")
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                name="Jane Doe",
                username=new_user,
                email="janedoe@gmail.com",  # Duplicate email
                allocated=False
            )

        # Test: Allocated default value is False
    def test_default_allocated_is_false(self):
        student = Student(
            name="Jane Doe",
            username= self.user,
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

 # Test: Payment must be one of the valid choices
    def test_valid_payment_status(self):
        # Test valid payment status "Pending"
        self.student.payment = "Pending"
        self.student.full_clean()  # Should not raise validation error
        self.student.save()

        # Test valid payment status "Successful"
        self.student.payment = "Successful"
        self.student.full_clean()  # Should not raise validation error
        self.student.save()

    def test_invalid_payment_status(self):
        # Test invalid payment status should raise ValidationError
        self.student.payment = "InvalidStatus"
        with self.assertRaises(ValidationError):
            self.student.full_clean()

    def test_default_payment_status(self):
        # Test default payment status is set to "Pending" (if applicable)
        student_no_payment = Student(
            name="Jane Doe",
            username=self.user,
            email="jane.doe@gmail.com",
            allocated=False
        )
        student_no_payment.full_clean()  # Should pass validation
        student_no_payment.save()
        self.assertEqual(student_no_payment.payment, "Pending")  # Default payment status should be "Pending"

        # Test: String representation (__str__)
    def test_string_representation(self):
        expected_str = f"{self.student.name} ({self.student.username.username}) ({self.student.email}), Allocated? {'Yes' if self.student.allocated else 'No'}, Payment Status: {self.student.payment}"
        self.assertEqual(str(self.student), expected_str)


        # Test: Description method
    def test_description(self):
        allocation_status = 'allocated' if self.student.allocated else 'not allocated'
        expected_description = f"{self.student.name} ({self.student.username.username}) is {allocation_status} and has payment status {self.student.payment}."
        self.assertEqual(self.student.description(), expected_description)


    def test_valid_student_instance_can_be_saved(self):
        self.student.full_clean()  # Validate the instance
        self.student.save()
        self.assertEqual(Student.objects.count(), 1)

