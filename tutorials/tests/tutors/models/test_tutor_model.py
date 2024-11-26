from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tutorials.models import Tutor, User
from tutorials.forms import TutorForm

class TutorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="janedoe")

        self.tutor = Tutor(
            name="Jane Doe",
            username = self.user,
            email="janedoe@gmail.com",
            subject="Java"
        )

    def test_blank_name_is_invalid(self):
        self.tutor.name = ""
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_blank_email_is_invalid(self):
        self.tutor.email = ""
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_blank_subject_is_invalid(self):
        self.tutor.subject = ""
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
        another_tutor = Tutor(
            name="Jane Doe",
            username=self.user,  # Same user reference
            email="jane.doe2@gmail.com",
            subject="Java"
        )
        another_tutor.full_clean()  # Should not raise validation error
        another_tutor.save()
        self.assertEqual(Tutor.objects.count(),2)

    def test_tutor_email_must_be_unique(self):
        self.tutor.save()
        new_user = User.objects.create(username="janedoe2", email="janedoe2@gmail.com")
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(
                name="Jane Doe",
                username = new_user,
                email = "janedoe@gmail.com",
                subject="Java",
            )

    def test_case_insensitive_email_is_invalid(self):
        #creates tutor with an already existing email
        new_user = User.objects.create(username = "janedoe2", email = "janedoe2@gmail.com")
        Tutor.objects.create(
            name = "John Smith", username = new_user, email = "janedoe2@gmail.com", subject = "Java"
        )
        #attempts to submit the form with the same email but different case
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    