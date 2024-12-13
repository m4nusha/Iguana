from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, User

INVALID_STUDENT_ID = 0

class DeleteStudentTestCase(TestCase):
    def setUp(self):
        # Create a User instance
        self.user = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
            user_type="not specified"
        )

        self.client.login(username="@janedoe", password="password123")

        # Create a second User instance
        self.another_user = User.objects.create_user(
            username="@johnsmith",
            email="johnsmith@example.com",
            password="password456",
            user_type="not specified"
        )

        # Create a Student instance referencing the User instance
        self.student = Student.objects.create(
            name="Jane Doe",
            username=self.user,
            email="janedoe@student.example.com",
            allocated=True,
            payment="Successful"
        )

        # Create another Student instance
        self.another_student = Student.objects.create(
            name="John Smith",
            username=self.another_user,
            email="johnsmith@student.example.com",
            allocated=False,
            payment="Pending"
        )

        # URL for the delete_student view
        self.url = reverse('delete_student', kwargs={'student_id': self.student.id})
        self.invalid_url = reverse('delete_student', kwargs={'student_id': INVALID_STUDENT_ID})
        self.another_student_url = reverse('delete_student', kwargs={'student_id': self.another_student.id})

    def test_delete_student_url(self):
        self.assertEqual(self.url, f'/delete_student/{self.student.id}/')

    def test_get_delete_student(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/delete_student.html')

    def test_get_delete_student_with_invalid_pk(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_id(self):
        student_id = self.student.id
        before_count = Student.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count - 1)
        expected_redirect_url = reverse('students_list')  # Redirect to the list of students
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(pk=student_id)

    def test_post_with_invalid_pk(self):
        before_count = Student.objects.count()
        response = self.client.post(self.invalid_url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_student(self):
        nonexistent_url = reverse('delete_student', kwargs={'student_id': 9999})
        response = self.client.post(nonexistent_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_delete_student_owned_by_another_user(self):
        # Attempt to delete another user's student
        response = self.client.post(self.another_student_url, follow=True)
        expected_redirect_url = reverse('students_list')  # Redirect to the list of students
        self.assertRedirects(response, expected_redirect_url, status_code=302)
