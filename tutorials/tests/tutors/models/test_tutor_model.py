from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tutorials.models import Tutor, User, Subject
from tutorials.forms import TutorForm
from decimal import Decimal

class TutorTestCase(TestCase):
    def setUp(self):
        self.python_subject, created = Subject.objects.get_or_create(name = "Python")
        self.java_subject, created = Subject.objects.get_or_create(name = "Java")
        
        # Create User instances for testing
        self.user1 = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            username="@johnsmith",
            email="johnsmith@example.com",
            password="password123",
        )

        # Create a Tutor instance for testing
        self.tutor = Tutor.objects.create(
            name="Jane Doe",
            username=self.user1,
            email="janedoe@student.example.com",
            rate = Decimal("30.00"),
        )
        self.tutor.subjects.add(self.python_subject)
        self.tutor.subjects.add(self.java_subject)

        self.form_input = {
            'name': "Jane Updated",
            'username': self.user2,  #use a new User instance
            'email': "updated@example.com",
            'rate': Decimal("35.00"),
            'subjects': [self.python_subject],
        }


    def test_duplicate_email_is_invalid(self):
        """Test that duplicate email addresses are invalid."""
        #create a tutor with the same email as in the form input
        Tutor.objects.create(
            name="John Smith",
            username=self.user2,
            email="janedoe@example.com",  #same email as in the form input
            rate=30.00,
        )
        self.form_input['email'] = "janedoe@example.com"
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid(), "The form should be invalid due to duplicate email.")
        self.assertIn('email', form.errors, "There should be an error for the email field.")


    def test_duplicate_username_is_invalid(self):
        """Test that duplicate usernames are invalid."""
        #create a tutor with the same username as in the form input
        Tutor.objects.create(
            name="John Smith",
            username=self.user2,  #same username as in the form input
            email="johnsmith@gmail.com",
            rate=30.00,
        )
        self.form_input['username'] = self.user2

        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid(), "The form should be invalid due to duplicate username.")
        self.assertIn('username', form.errors, "There should be an error for the username field.")


    def test_valid_tutor_instance_can_be_saved(self):
        self.tutor.full_clean()
        self.tutor.save()
        self.assertEqual(Tutor.objects.count(), 1)

    def test_string_representation(self):
        expected_str = f"{self.tutor.name} ({self.tutor.username})"
        self.assertEqual(str(self.tutor), expected_str)


    def test_tutor_can_reference_same_username(self):
        """Test: Username uniqueness (handled by the User model, not Tutor)"""
        #create another tutor referencing the same username (ForeignKey)
        self.tutor.save()
        another_tutor = Tutor(
            name="Jane Doe",
            username=self.user1,  #same user reference
            email="janedoe@example.com",
            rate = Decimal("25.00"),
        )
        another_tutor.full_clean()  #should not raise validation error
        another_tutor.save()
        self.assertEqual(Tutor.objects.count(),2)

    def test_valid_rate_is_accepted(self):
        """Test that a valid rate is accepted and the tutor can be saved."""
        self.tutor.rate = Decimal("50.00")  #assign a valid rate
        try:
            self.tutor.full_clean()  #validate the model instance
            self.tutor.save()  #save the instance
        except ValidationError as e:
            self.fail(f"Valid rate should not raise ValidationError: {e}")
    
        #assert that the tutor was saved successfully
        self.assertEqual(Tutor.objects.count(), 1, "Tutor with a valid rate was not saved successfully.")


    def test_negative_rate_is_invalid(self):
        """Test that a negative rate is invalid."""
        self.tutor.rate = Decimal("-10.00")
        with self.assertRaises(ValidationError) as context:
            self.tutor.full_clean()

        self.assertIn('rate', context.exception.message_dict, "ValidationError should be raised for the 'rate' field.")

    def test_zero_rate_is_invalid(self):
        """Test that a zero rate is invalid (minimum valid rate is 0.01)."""
        self.tutor.rate = Decimal("0.00")  #set rate to zero
        with self.assertRaises(ValidationError):  #expecting a ValidationError
            self.tutor.full_clean()

    def test_maximum_rate_is_accepted(self):
        """Test that the maximum valid rate (9999.99) is accepted."""
        self.tutor.rate = Decimal("9999.99")
        self.tutor.full_clean()
        self.tutor.save()
        self.assertEqual(self.tutor.rate, Decimal("9999.99"))

    def test_excessively_high_rate_is_invalid(self):
        """Test that an excessively high rate (e.g., 10000.00) is invalid."""
        self.tutor.rate = Decimal("10000.00")
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_rate_precision_is_enforced(self):
        """Test that the rate does not allow more than two decimal places."""
        self.tutor.rate = Decimal("25.555")  #invalid precision
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_multiple_subjects_are_valid(self):
        """Test that a tutor can have multiple subjects associataed"""
        self.tutor.subjects.add(self.python_subject, self.java_subject)
        self.tutor.full_clean()
        self.assertEqual(self.tutor.subjects.count(),2)


    


    