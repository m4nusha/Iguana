from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, User
from unittest.mock import patch


class UpdateStudentViewTest(TestCase):

    def setUp(self):
        # Create a user and a student for testing
        self.user = User.objects.create_user(
            username='@testuser', first_name='Test', last_name='User',password="password123" ,email='testuser@example.com', user_type='not specified')

        self.client.login(username="@testuser", password="password123")

        self.student = Student.objects.create(
            name="Old Name", username=self.user, email="oldemail@example.com")
        self.url = reverse('update_student', args=[self.student.id])

    def test_valid_student_update(self):
        """Test that valid student updates work as expected."""
        data = {
            'name': 'Updated Name',
            'username': self.student.username.id,  # Use the User ID for username
            'email': 'updatedemail@example.com',
            'allocated': self.student.allocated,
            'payment': self.student.payment
        }
        response = self.client.post(self.url, data)

        # Reload the student from the database to check if the values are updated
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'Updated Name')
        self.assertEqual(self.student.email, 'updatedemail@example.com')
        self.assertRedirects(response, reverse('students_list'))

    def test_student_not_found(self):
        """Test that a 404 error is returned if the student does not exist."""
        non_existing_student_id = 9999
        url = reverse('update_student', args=[non_existing_student_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_invalid_student_update(self):
        """Test that invalid form submission (e.g., invalid email) results in form errors."""
        data = {
            'name': 'Updated Name',
            'username': self.student.username.id,
            'email': 'invalidemail',  # Invalid email
            'allocated': self.student.allocated,
            'payment': self.student.payment
        }
        response = self.client.post(self.url, data)

        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')

    @patch('tutorials.forms.StudentForm.save')
    def test_database_save_error(self, mock_save):
        """Test that the user is informed if there's an error when saving the student."""
        mock_save.side_effect = Exception('Database save error')

        data = {
            'name': 'Updated Name',
            'username': self.student.username.id,
            'email': 'updatedemail@example.com',
            'allocated': self.student.allocated,
            'payment': self.student.payment
        }
        response = self.client.post(self.url, data)

        self.assertFormError(response, 'form', None,
                             "It was not possible to save this student to the database, Database save error")

    def test_get_request_prefills_form(self):
        """Test that the form is pre-filled with the student's current data on GET request."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.name)
        self.assertContains(response, self.student.email)
