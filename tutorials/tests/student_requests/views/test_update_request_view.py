from django.test import TestCase
from django.urls import reverse
from tutorials.models import StudentRequest, User
from tutorials.forms import StudentRequestForm

INVALID_REQUEST_ID = 0

class UpdateRequestTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
            user_type= 'not specified'
        )

        self.client.login(username="@janedoe", password="password123")

        # Create a test StudentRequest instance
        self.student_request = StudentRequest.objects.create(
            name="Jane Doe",
            username=self.user,
            request_type="profile_update",
            description="Update my profile picture.",
            status="pending",
            priority="low"
        )

        # Define valid form input
        self.form_input = {
            'username': self.user.id,
            'request_type': "password_reset",
            'description': "I forgot my password.",
            'status': "in_progress",
            'priority': "medium"
        }

        # URL for the update_request view
        self.url = reverse('update_request', kwargs={'request_id': self.student_request.id})

    def test_update_request_url(self):
        """Test that the update_request URL resolves correctly."""
        self.assertEqual(self.url, f'/update_request/{self.student_request.id}/')

    def test_get_update_request(self):
        """Test the GET request to edit a student request."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/update_request.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentRequestForm))
        self.assertFalse(form.is_bound)

    def test_get_update_request_with_invalid_id(self):
        """Test the GET request with an invalid student request ID."""
        invalid_url = reverse('update_request', kwargs={'request_id': INVALID_REQUEST_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_data(self):
        """Test the POST request to update a student request with valid data."""
        request_id = self.student_request.id
        before_count = StudentRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count)  # No new requests should be created
        expected_redirect_url = reverse('student_requests')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        updated_request = StudentRequest.objects.get(pk=request_id)
        self.assertEqual(self.form_input['request_type'], updated_request.request_type)
        self.assertEqual(self.form_input['description'], updated_request.description)
        self.assertEqual(self.form_input['status'], updated_request.status)
        self.assertEqual(self.form_input['priority'], updated_request.priority)

    def test_post_with_invalid_form_data(self):
        """Test the POST request with invalid form data."""
        self.form_input['description'] = ''  # Make the description invalid
        before_count = StudentRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/update_request.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentRequestForm))
        self.assertTrue(form.is_bound)
        self.assertIn('description', form.errors)

    def test_post_with_duplicate_request_type(self):
        """Test the POST request with a duplicate request_type for the same user."""
        # Create another request with the same type
        StudentRequest.objects.create(
            name="Jane Doe",
            username=self.user,
            request_type="password_reset",
            description="Another request.",
            status="pending",
            priority="low"
        )
        before_count = StudentRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/update_request.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentRequestForm))
        self.assertTrue(form.is_bound)
        self.assertIn('request_type', form.errors)
        self.assertIn('already exists', form.errors['request_type'][0])
