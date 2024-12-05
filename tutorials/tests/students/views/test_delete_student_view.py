from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, User

INVALID_STUDENT_ID = 0

class DeleteStudentTestCase(TestCase):
    def setUp(self):
        # Create a User instance with user_type='student'
        self.user = User.objects.create_user(
            username="@johndoe",
            email="johndoe@example.com",
            password="password123",
            user_type="student"
        )

        # Fetch the automatically created Student instance
        self.student = Student.objects.get(username=self.user)

        # Update additional fields for the Student instance
        self.student.name = "John Doe"
        self.student.allocated = True
        self.student.payment = "Successful"
        self.student.save()

        # Formulate the URL for the delete_student view
        self.url = reverse('delete_student', kwargs={'student_id': self.student.id})

    def test_delete_student_url(self):
        self.assertEqual(self.url, f'/delete_student/{self.student.id}/')

    def test_get_delete_student(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_student.html')

    def test_get_delete_student_with_invalid_pk(self):
        invalid_url = reverse('delete_student', kwargs={'student_id': INVALID_STUDENT_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_id(self):
        student_id = self.student.id
        before_count = Student.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count - 1)
        expected_redirect_url = reverse('students')  # Redirect to the list of students
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(pk=student_id)

    def test_post_with_invalid_pk(self):
        invalid_url = reverse('delete_student', kwargs={'student_id': INVALID_STUDENT_ID})
        before_count = Student.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)
