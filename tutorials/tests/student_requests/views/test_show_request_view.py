from django.test import TestCase
from django.urls import reverse
from tutorials.models import StudentRequest, User

class ShowRequestTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="@janedoe",
            email="johndoe@example.com",
            password="password123",
            user_type='not specified',
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

        # Define the URL for the show_request view
        self.url = reverse('show_request', kwargs={'request_id': self.student_request.id})

    def test_show_request_url(self):
        """Test that the show_request URL resolves correctly."""
        self.assertEqual(self.url, f'/requests/{self.student_request.id}/')

    def test_get_show_request_valid(self):
        """Test the GET request for a valid student request."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students_requests/show_request.html')
        self.assertIn('student_request', response.context)
        student_request = response.context['student_request']
        self.assertEqual(student_request.id, self.student_request.id)  # Ensure the correct request is passed

    def test_get_show_request_invalid(self):
        """Test the GET request with an invalid student request ID."""
        invalid_url = reverse('show_request', kwargs={'request_id': 9999})  # Invalid request ID
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)  # Check for Http404 response
