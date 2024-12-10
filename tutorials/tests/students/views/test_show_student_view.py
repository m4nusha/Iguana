from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, User

class ShowStudentTestCase(TestCase):
    def setUp(self):
        # Create a User instance with user_type='student'
        self.user = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
            user_type="student"
        )

        # Fetch the automatically created Student instance
        self.student = Student.objects.get(username=self.user)

        # Update additional fields for the Student instance
        self.student.name = "Jane Doe"
        self.student.allocated = True
        self.student.payment = "Successful"
        self.student.save()

        # Formulate the URL for the delete_student view
        self.url = reverse('show_student', kwargs={'student_id': self.student.id})

    def test_show_student_url(self):
        self.assertEqual(self.url, f'/students/{self.student.id}/')  # Verify the URL is correct

    def test_get_show_student_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_student.html')
        self.assertIn('student', response.context)
        student = response.context['student']
        self.assertEqual(student.id, self.student.id)  # Ensure the correct student is passed
        self.assertEqual(student.username, self.user)

    def test_get_show_student_invalid(self):
        invalid_url = reverse('show_student', kwargs={'student_id': 9999})  # Invalid student ID
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)  # Check for Http404 response
