from django.test import TestCase
from tutorials.forms import TutorForm
from tutorials.models import Tutor

class TutorFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'name': "Doe, J.",
            'username': "janedoe",
            'email': "janedoe@gmail.com",
            'subject': "Math"
        }

    # Test cases
    def test_valid_form(self):
        form = TutorForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = TutorForm()
        self.assertIn('name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('subject', form.fields)

    def test_blank_name_is_invalid(self):
        self.form_input['name'] = ""
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_subject_is_invalid(self):
        self.form_input['subject'] = ""
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_email_is_invalid(self):
        self.form_input['email'] = ""
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_duplicate_email_is_invalid(self):
        Tutor.objects.create(
            name="John Smith", username="johnsmith", email="janedoe@gmail.com", subject="Physics"
        )
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_duplicate_username_is_invalid(self):
        Tutor.objects.create(
            name="John Smith", username="janedoe", email="johnsmith@gmail.com", subject="Physics"
        )
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())