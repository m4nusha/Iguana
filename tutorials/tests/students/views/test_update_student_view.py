from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.http import Http404

from tutorials.forms import StudentForm
from tutorials.models import Student

INVALID_STUDENT_ID = 0


class UpdateStudentTestCase(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="John Doe",
            username="johndoe",
            email="john.doe@example.com",
            allocated=True,
        )
        self.form_input = {
            'name': "John Doe Jr.",
            'username': "johndoejr",  # New username for update
            'email': "john.doe.jr@example.com",
            'allocated': True,
        }
        self.url = reverse('update_student', kwargs={'student_id': self.student.id})

    def test_update_student_url(self):
        self.assertEqual(self.url, f'/update_student/{self.student.id}')

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
        student_id = self.student.id
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

    def test_post_with_non_unique_username(self):
        # Create another student with a conflicting username
        Student.objects.create(
            name="Alice Doe",
            username="johndoejr",  # Duplicate username
            email="alice.doe@example.com",
            allocated=True,
        )

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
        self.assertIn('username', form.errors)  # Check if 'username' field has errors

    def test_post_with_non_unique_email(self):
        # Create another student with a conflicting email
        Student.objects.create(
            name="Jane Doe",
            username="janedoe",
            email="john.doe.jr@example.com",  # Duplicate email
            allocated=True,
        )

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
