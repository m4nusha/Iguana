from django.test import TestCase
from tutorials.models import User, StudentRequest
from tutorials.forms import StudentRequestForm

class StudentRequestFormTestCase(TestCase):
    def setUp(self):
        # Set up a test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Define valid form input
        self.form_input = {
            'username': self.user.id,
            'request_type': 'profile_update',
            'description': 'Request to update my profile picture.',
            'status': 'pending',
            'priority': 'low'
        }

    def test_valid_form(self):
        """Test that the form is valid with correct data."""
        form = StudentRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_missing_request_type(self):
        """Test that the form is invalid without a request type."""
        self.form_input['request_type'] = ''
        form = StudentRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('request_type', form.errors)

    def test_missing_description(self):
        """Test that the form is invalid without a description."""
        self.form_input['description'] = ''
        form = StudentRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_invalid_request_type(self):
        """Test that the form is invalid with an incorrect request type."""
        self.form_input['request_type'] = 'invalid_request_type'
        form = StudentRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('request_type', form.errors)

    def test_duplicate_request_type_for_user(self):
        """Test that the form is invalid if a user has an existing request of the same type."""
        # Create an existing StudentRequest
        StudentRequest.objects.create(
            username=self.user,
            request_type='profile_update',
            description='Existing request',
            status='pending',
            priority='medium'
        )
        form = StudentRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('request_type', form.errors)
        self.assertIn('already exists', form.errors['request_type'][0])

    def test_invalid_priority(self):
        """Test that the form is invalid with an incorrect priority."""
        self.form_input['priority'] = 'urgent'
        form = StudentRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('priority', form.errors)

    def test_invalid_status(self):
        """Test that the form is invalid with an incorrect status."""
        self.form_input['status'] = 'not_valid_status'
        form = StudentRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

    def test_save_populates_name(self):
        """Test that saving the form populates the name field with the user's full name."""
        form = StudentRequestForm(data=self.form_input)
        if form.is_valid():
            request = form.save(commit=False)
            self.assertEqual(request.name, self.user.get_full_name())
