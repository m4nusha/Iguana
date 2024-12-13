from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, StudentRequest, User
from tutorials.tests.student_requests.views.test_update_request_view import INVALID_REQUEST_ID

INVALID_STUDENT_ID = 0

class DeleteStudentTestCase(TestCase):
    def setUp(self):
        # Set up a test user and student instance
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.student = Student.objects.create(
            name="John Doe",
            username=self.user,
            email="john.doe@example.com",
            allocated=True,
            payment='Pending',
        )
        self.url = reverse('delete_student', kwargs={'student_id': self.student.id})

    def test_delete_student_url(self):
        """Test that the delete student URL resolves correctly."""
        self.assertEqual(self.url, f'/delete_student/{self.student.id}/')

    def test_get_delete_student(self):
        """Test the GET request for deleting a student."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_student.html')

    def test_get_delete_student_with_invalid_id(self):
        """Test the GET request with an invalid student ID."""
        invalid_url = reverse('delete_student', kwargs={'student_id': INVALID_STUDENT_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_delete_student(self):
        """Test the POST request to delete a student."""
        student_id = self.student.id
        before_count = Student.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count - 1)
        expected_redirect_url = reverse('students')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(pk=student_id)

    def test_post_delete_student_with_invalid_id(self):
        """Test the POST request with an invalid student ID."""
        invalid_url = reverse('delete_student', kwargs={'student_id': INVALID_STUDENT_ID})
        before_count = Student.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)

    def test_get_delete_request_with_invalid_id(self):
        invalid_url = reverse('delete_request', kwargs={'request_id': INVALID_REQUEST_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_delete_request_with_invalid_id(self):
        invalid_url = reverse('delete_request', kwargs={'request_id': INVALID_REQUEST_ID})
        before_count = StudentRequest.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = StudentRequest.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)

    def test_delete_request_with_invalid_request_id(self):
        invalid_url = reverse('delete_request', kwargs={'request_id': INVALID_REQUEST_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)