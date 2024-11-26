from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student

class StudentsListTestCase(TestCase):
    def setUp(self):
        # Create some students for testing
        self.student1 = Student.objects.create(
            name="John Doe",
            username="johndoe",
            email="johndoe@example.com",
            allocated=True
        )
        self.student2 = Student.objects.create(
            name="Jane Smith",
            username="janesmith",
            email="janesmith@example.com",
            allocated=True
        )
        self.url = reverse('students')  # URL for the students list view

    def test_students_url(self):
        self.assertEqual(self.url, '/students/')  # Verify the URL is correct

    def test_get_students(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students.html')
        self.assertIn('students', response.context)
        students = response.context['students']
        self.assertEqual(students.count(), 2)  # Ensure both students are in the context
