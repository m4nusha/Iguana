from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from tutorials.models import Tutor

class TutorTestCase(TestCase):
    def setUp(self):
        self.tutor = Tutor(
            name="Doe, J.",
            username="janedoe",
            email="janedoe@gmail.com",
            subject="Math"
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
                name="John Smith", username="johnsmith", email="janedoe@gmail.com", subject="Physics"
            )

    def test_duplicate_username_is_invalid(self):
        self.tutor.save()
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(
                name="John Smith", username="janedoe", email="johnsmith@gmail.com", subject="Physics"
            )

    def test_valid_tutor_instance_can_be_saved(self):
        self.tutor.full_clean()
        self.tutor.save()
        self.assertEqual(Tutor.objects.count(), 1)

    def test_string_representation(self):
        expected_str = f"{self.tutor.name} ({self.tutor.username})"
        self.assertEqual(str(self.tutor), expected_str)