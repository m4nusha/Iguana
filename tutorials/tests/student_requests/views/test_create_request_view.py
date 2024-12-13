from django.test import TestCase
from django.urls import reverse
from tutorials.forms import StudentRequestForm
from tutorials.models import StudentRequest, User

class CreateRequestTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='@janedoe',
            email='janedoe@example.com',
            password='password123'
        )
        self.client.login(username="@janedoe", password="password123")

        self.url = reverse('create_request')  # URL for the create_request view
        self.form_input = {
            'username': self.user.id,
            'request_type': 'profile_update',
            'description': 'I want to update my profile picture.',
            'status': 'pending',
            'priority': 'low',
        }

    def test_create_request_url(self):
        """Test that the create_request URL resolves correctly."""
        self.assertEqual(self.url, '/create_request/')

    def test_get_create_request(self):
        """Test the GET request to render the create request form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/create_request.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentRequestForm))
        self.assertFalse(form.is_bound)

    def test_post_with_valid_data(self):
        """Test the POST request to create a new student request with valid data."""
        before_count = StudentRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count + 1)

        expected_redirect_url = reverse('student_requests')  # Redirect to the list of requests
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_post_with_invalid_data(self):
        """Test the POST request with invalid form data."""
        # Make the description field blank
        self.form_input['description'] = ''
        before_count = StudentRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count)  # No new request should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/create_request.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentRequestForm))
        self.assertTrue(form.is_bound)
        self.assertIn('description', form.errors)  # Check if 'description' field has errors

    def test_post_with_duplicate_request_type(self):
        """Test the POST request with a duplicate request type for the same user."""
        # Create an existing request with the same type
        StudentRequest.objects.create(
            name="Jane Doe",
            username=self.user,
            request_type='profile_update',
            description='Existing request.',
            status='pending',
            priority='low'
        )
        before_count = StudentRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count)  # No new request should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/create_request.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentRequestForm))
        self.assertTrue(form.is_bound)
        self.assertIn('request_type', form.errors)  # Check if 'request_type' field has errors
