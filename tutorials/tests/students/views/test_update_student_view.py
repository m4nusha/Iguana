from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.http import Http404

from tutorials.forms import StudentForm
from tutorials.models import Student, User

INVALID_STUDENT_ID = 0


class UpdateStudentTestCase(TestCase):
    def setUp(self):
        # Create User instances with user_type='student'
        self.user1 = User.objects.create_user(
            username="@johndoe",
            email="johndoe@example.com",
            password="password123",
            user_type="student"
        )

        # Fetch the automatically created Student instance
        self.student1 = Student.objects.get(username=self.user1)

        # Update additional fields for Student instance
        self.student1.name = "John Doe"
        self.student1.allocated = True
        self.student1.payment = "Successful"
        self.student1.save()

        self.form_input = {
            'name': "John Doe Jr.",
            'username': "johndoejr",  # New username for update
            'email': "john.doe.jr@example.com",
            'allocated': True,
            'payment': "Pending",
        }

        self.url = reverse('update_student', kwargs={'student_id': self.student1.id})

    def test_update_student_url(self):
        self.assertEqual(self.url, f'/update_student/{self.student1.id}/')

    def test_get_update_student(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_student.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertFalse(form.is_bound)

    def test_get_update_student_with_invalid_pk(self):
        invalid_url = reverse('update_student', kwargs={'student_id': INVALID_STUDENT_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_data(self):
        student_id = self.student1.id
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)  # No new student added
        expected_redirect_url = reverse('students')  # Redirect to the student list page
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

        student = Student.objects.get(pk=student_id)
        self.assertEqual(self.form_input['name'], student.name)
        self.assertEqual(self.form_input['username'], student.username)
        self.assertEqual(self.form_input['email'], student.email)
        self.assertEqual(self.form_input['allocated'], student.allocated)
        self.assertEqual(self.form_input['payment'], student.payment)

    def test_post_with_invalid_pk(self):
        invalid_url = reverse('update_student', kwargs={'student_id': INVALID_STUDENT_ID})
        before_count = Student.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)  # No new student added
        self.assertEqual(response.status_code, 404)

    def test_post_with_invalid_form_data(self):
        self.form_input['name'] = ''  # Invalid form data (name is required)
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)  # No new student added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_student.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertTrue(form.is_bound)

    def test_post_with_non_unique_email(self):
        # Create User instances with user_type='student'
        self.user1 = User.objects.create_user(
            username="@janedoe",
            email="john.doe.jr@example.com",  # Conflicting email
            password="password123",
            user_type="student"
        )

        # Fetch the automatically created Student instance
        self.student1 = Student.objects.get(username=self.user1)

        # Update additional fields for Student instance
        self.student1.name = "Jane Doe"
        self.student1.allocated = True
        self.student1.payment = "Successful"
        self.student1.save()

        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()

        self.assertEqual(after_count, before_count)  # No new student should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_student.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertTrue(form.is_bound)
        self.assertIn('email', form.errors)  # Check if 'email' field has errors

