from django.test import TestCase
from tutorials.forms import TutorForm
from tutorials.models import Tutor, User, Subject
from django.core.exceptions import ValidationError

class TutorFormTestCase(TestCase):
    def setUp(self):
        self.subject1 = Subject.objects.create(name = "Python")
        self.subject2 = Subject.objects.create(name = "Java")
        self.form_input = {
            'name': "Doe, J.",
            'username': "janedoe",
            'email': "janedoe@gmail.com",
            'subjects': [self.subject1.id, self.subject2.id] #pass subject ids
        }

    # Test cases
    def test_valid_form(self):
        form = TutorForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    #!!!!!!!
    def test_form_has_necessary_fields(self):
        form = TutorForm()
        self.assertIn('name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('subject', form.fields)
    #!!!!!!!

    def test_blank_name_is_invalid(self):
        self.form_input['name'] = ""
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_subject_is_invalid(self):
        self.form_input['subjects'] = []   #no subjects selected
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_email_is_invalid(self):
        self.form_input['email'] = ""
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    #!!!!!!!
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
    #!!!!!!!


    # Test: Username must be a valid User
    def test_username_must_be_valid_user(self):
        self.tutor.username = None  # Setting username to None
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    #!!!!!!!
    # Test: Username uniqueness (handled by the User model, not Tutor)
    def test_tutor_can_reference_same_username(self):
        # Create another tutor referencing the same username (ForeignKey)
        self.tutor.save()
        another_tutor = Tutor(
            name="Jane Doe",
            username=self.user,  # Same user reference
            email="jane.doe2@gmail.com",
            subject = "Java"
        )
        another_tutor.full_clean()  # Should not raise validation error
        another_tutor.save()
        self.assertEqual(Tutor.objects.count(),2)