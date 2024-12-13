from django.test import TestCase
from django.urls import reverse
from tutorials.models import StudentRequest, User

class StudentRequestsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
            user_type="student"
        )
        self.client.login(username="@janedoe", password="password123")

        # Create test StudentRequest instances
        self.request1 = StudentRequest.objects.create(
            name="Jane Doe",
            username=self.user,
            request_type="profile_update",
            description="Update my profile picture.",
            status="pending",
            priority="low"
        )
        self.request2 = StudentRequest.objects.create(
            name="Jane Smith",
            username=self.user,
            request_type="password_reset",
            description="Reset my password.",
            status="in_progress",
            priority="medium"
        )
        self.request3 = StudentRequest.objects.create(
            name="Alice Johnson",
            username=self.user,
            request_type="course_enrollment",
            description="Enroll me in the course.",
            status="resolved",
            priority="high"
        )

        self.url = reverse("student_requests")  # URL for the student_requests view

    def test_student_requests_url(self):
        """Test that the student_requests URL resolves correctly."""
        self.assertEqual(self.url, "/requests/")

    def test_get_student_requests(self):
        """Test the GET request to display all student requests."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students_requests/student_requests.html")
        self.assertIn("requests", response.context)
        requests = response.context["requests"]
        self.assertEqual(requests.count(), 3)  # Ensure all requests are in the context

    def test_filter_by_status(self):
        """Test filtering requests by status."""
        response = self.client.get(self.url, {"status": "pending"})
        requests = response.context["requests"]
        self.assertEqual(requests.count(), 1)  # Only "pending" requests should appear
        self.assertTrue(all(request.status == "pending" for request in requests))

    def test_filter_by_priority(self):
        """Test filtering requests by priority."""
        response = self.client.get(self.url, {"priority": "medium"})
        requests = response.context["requests"]
        self.assertEqual(requests.count(), 1)  # Only "medium" priority requests should appear
        self.assertTrue(all(request.priority == "medium" for request in requests))

    def test_filter_by_request_type(self):
        """Test filtering requests by request type."""
        response = self.client.get(self.url, {"request_type": "course_enrollment"})
        requests = response.context["requests"]
        self.assertEqual(requests.count(), 1)  # Only "course_enrollment" requests should appear
        self.assertTrue(all(request.request_type == "course_enrollment" for request in requests))

    def test_search_by_name(self):
        """Test searching for requests by name."""
        response = self.client.get(self.url, {"search": "Alice"})
        requests = response.context["requests"]
        self.assertEqual(requests.count(), 1)  # Only the request with "Alice" in the name
        self.assertEqual(requests[0].name, "Alice Johnson")

    def test_sort_by_name_ascending(self):
        """Test sorting requests by name in ascending order."""
        response = self.client.get(self.url, {"order_by": "asc"})
        requests = response.context["requests"]
        self.assertEqual(requests[0].name, "Alice Johnson")  # A-Z order
        self.assertEqual(requests[1].name, "Jane Doe")
        self.assertEqual(requests[2].name, "Jane Smith")

    def test_sort_by_name_descending(self):
        """Test sorting requests by name in descending order."""
        response = self.client.get(self.url, {"order_by": "desc"})
        requests = response.context["requests"]
        self.assertEqual(requests[0].name, "Jane Smith")  # Z-A order
        self.assertEqual(requests[1].name, "Jane Doe")
        self.assertEqual(requests[2].name, "Alice Johnson")
