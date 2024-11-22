from django.test import TestCase
from django.urls import reverse
from tutorials.forms import StudentForm
from tutorials.models import Student

class CreateStudentTestCase(TestCase):
    def setUp(self):
        self.url = reverse('create_student')  # URL for the create_student view
        self.form_input = {
            'name': 'Doe, J.',
            'username': 'janedoe',
            'email': 'janedoe@gmail.com',
            'allocated': True
        }

    def test_create_student_url(self):
        self.assertEqual(self.url, '/create_student/')

    def test_get_create_student(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_student.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertFalse(form.is_bound)

    def test_post_with_valid_data(self):
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count + 1)

        expected_redirect_url = reverse('students')  # Redirect to the list of students
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_post_with_invalid_data(self):
        # Make the name field blank
        self.form_input['name'] = ''
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)  # No new student should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_student.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertTrue(form.is_bound)
        self.assertIn('name', form.errors)  # Check if 'name' field has errors

    def test_post_with_duplicate_username(self):
        # Create an existing student with the same username
        Student.objects.create(
            name='Existing Student',
            username='janedoe',  # Duplicate username
            email='existinguser@gmail.com',
            allocated=True
        )
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)  # No new student should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_student.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertTrue(form.is_bound)
        self.assertIn('username', form.errors)  # Check if 'username' field has errors

    def test_post_with_duplicate_email(self):
        # Create an existing student with the same email
        Student.objects.create(
            name='Existing Student',
            username='existinguser',
            email='janedoe@gmail.com',  # Duplicate email
            allocated=True
        )
        before_count = Student.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count, before_count)  # No new student should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_student.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, StudentForm))
        self.assertTrue(form.is_bound)
        self.assertIn('email', form.errors)  # Check if 'email' field has errors
