from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student

class ShowStudentTestCase(TestCase):
    def setUp(self):
        # Create a student for testing
        self.student = Student.objects.create(
            name="John Doe",
            username="johndoe",
            email="johndoe@example.com",
            allocated=True
        )
        self.url = reverse('show_student', kwargs={'student_id': self.student.id})

    def test_show_student_url(self):
        self.assertEqual(self.url, f'/students/{self.student.id}')  # Verify the URL is correct

    def test_get_show_student_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_student.html')
        self.assertIn('student', response.context)
        student = response.context['student']
        self.assertEqual(student.id, self.student.id)  # Ensure the correct student is passed

    def test_get_show_student_invalid(self):
        invalid_url = reverse('show_student', kwargs={'student_id': 9999})  # Invalid student ID
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)  # Check for Http404 response
