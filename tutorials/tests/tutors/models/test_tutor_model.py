from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tutorials.models import Tutor, User, Subject
from tutorials.forms import TutorForm

class TutorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="janedoe")

        self.subject1 = Subject.objects.create(name = "Python")
        self.subject2 = Subject.objects.create(name = "Java")

        self.tutor = Tutor.objects.create(
            name="Jane Doe",
            username = self.user,
            email="janedoe@gmail.com",
            rate = 25.50
        )
        self.tutor.subjects.add(self.subject1, self.subject2) #add subjects

    def test_blank_name_is_invalid(self):
        self.tutor.name = ""
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_blank_email_is_invalid(self):
        self.tutor.email = ""
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_blank_subject_is_invalid(self):
        self.tutor.subjects.clear()    #removes all subjects
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_duplicate_email_is_invalid(self):
        self.tutor.save()
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(
                name="John Smith", username="johnsmith", email="janedoe@gmail.com", subject="Python"
            )

    def test_duplicate_username_is_invalid(self):
        self.tutor.save()
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(
                name="John Smith", username="janedoe", email="johnsmith@gmail.com", subject="Python"
            )

    def test_valid_tutor_instance_can_be_saved(self):
        self.tutor.full_clean()
        self.tutor.save()
        self.assertEqual(Tutor.objects.count(), 1)

    def test_string_representation(self):
        expected_str = f"{self.tutor.name} ({self.tutor.username})"
        self.assertEqual(str(self.tutor), expected_str)


# Test: Username must be a valid User
    def test_username_must_be_valid_user(self):
        self.tutor.username = None  # Setting username to None
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()


    # Test: Username uniqueness (handled by the User model, not Tutor)
    def test_tutor_can_reference_same_username(self):
        # Create another student referencing the same username (ForeignKey)
        self.tutor.save()
        another_tutor = Tutor.objects.create(
            name="John Doe",
            username=self.user,  # Same user reference
            email="johndoe@gmail.com",
            rate = 20.00
        )
        another_tutor.subjects.add(self.subject2)
        another_tutor.save()
        self.assertEqual(Tutor.objects.count(),2)
        self.assertEqual(another_tutor.username, self.user)

    def test_tutor_email_must_be_unique(self):
        self.tutor.save()
        new_user = User.objects.create(username="janedoe2", email="janedoe2@gmail.com")
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(
                name="Jane Doe",
                username = new_user,
                email = "janedoe@gmail.com",   #duplicate email
                rate=20.00
            )

    def test_case_insensitive_email_is_invalid(self):
        """Tests that email uniqueness is case-sensitive"""
        new_user = User.objects.create(username = "janedoe2", email = "janedoe2@gmail.com")
        Tutor.objects.create(
            name = "John Smith",
            username = new_user,
            email = "JohnSmith@Gmail.com",
            rate = 20.00
        )
        #attempts to submit the form with the same email but different case
        form_data = {
            'name': "Duplicate Email",
            'username': new_user.id,
            'email': "johnsmith@gmail.com",
            'rate': 20.00,
            'subjects': [self.subject1.id]
        }
        form = TutorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_default_rate_is_set(self):
        """Test that the default rate is set to 10.00 if not specified."""
        tutor_with_default_rate = Tutor.objects.create(
            name="John Smith",
            username=self.user,
            email="johnsmith@gmail.com",
        )
        tutor_with_default_rate.subjects.add(self.subject2)
        tutor_with_default_rate.save()
        self.assertEqual(tutor_with_default_rate.rate, 10.00)


    def test_valid_rate_is_accepted(self):
        """Test that a valid rate is accepted and the tutor can be saved."""
        self.tutor.full_clean()  #should not raise any ValidationError
        self.tutor.save()
        self.assertEqual(Tutor.objects.count(), 1)

    def test_negative_rate_is_invalid(self):
        """Test that a negative rate is invalid."""
        self.tutor.rate = -10.00
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_zero_rate_is_valid(self):
        """Test that a zero rate is valid (if business rules allow it)."""
        self.tutor.rate = 0.00
        self.tutor.full_clean()
        self.tutor.save()
        self.assertEqual(self.tutor.rate, 0.00)

    def test_maximum_rate_is_accepted(self):
        """Test that the maximum valid rate (9999.99) is accepted."""
        self.tutor.rate = 9999.99
        self.tutor.full_clean()
        self.tutor.save()
        self.assertEqual(self.tutor.rate, 9999.99)

    def test_excessively_high_rate_is_invalid(self):
        """Test that an excessively high rate (e.g., 10000.00) is invalid."""
        self.tutor.rate = 10000.00
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_rate_precision_is_enforced(self):
        """Test that the rate does not allow more than two decimal places."""
        self.tutor.rate = 25.555  #invalid precision
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_multiple_subjects_are_valid(self):
        self.tutor.subjects.add(self.subject1, self.subject2)
        self.tutor.full_clean()
        self.assertEqual(self.tutor.subjects.count(),2)


    


    