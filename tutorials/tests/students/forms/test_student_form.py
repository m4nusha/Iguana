from django.test import TestCase
from tutorials.forms import StudentForm
from tutorials.models import Student

class StudentFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {
            'name': "Doe, J.",
            'username': "janedoe",
            'email': "janeDoe@gmail.com",  # Note the mixed case
            'allocated': True
        }

    # Test cases
    def test_valid_form(self):
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = StudentForm()
        self.assertIn('name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('allocated', form.fields)

    # Blank & too long testing for name and username
    def test_blank_name_is_invalid(self):
        self.form_input['name'] = ""
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overlong_name_is_invalid(self):
        self.form_input['name'] = 'x' * 256
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_username_is_invalid(self):
        self.form_input['username'] = ""
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overlong_username_is_invalid(self):
        self.form_input['username'] = 'x' * 256
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Blank, overlong, case sensitivity testing for email
    def test_blank_email_is_invalid(self):
        self.form_input['email'] = ""
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overlong_email_is_invalid(self):
        self.form_input['email'] = "x" * 255 + "@example.com"  # Exceeds the max_length of 254
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_case_insensitive_email_is_invalid(self):
        # Create a student with an existing email
        Student.objects.create(
            name="John Smith", username="johnsmith", email="janedoe@gmail.com", allocated=False
        )
        # Attempt to submit the form with the same email but different case
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Checkbox testing for allocated
    def test_checkbox_allocated_is_valid(self):
        form = StudentForm()
        self.assertIn('type="checkbox"', form.as_p())  # Check the HTML output contains a checkbox for allocated

    # Save() function test case
    def test_valid_form_can_be_saved(self):
        form = StudentForm(data=self.form_input)
        before_count = Student.objects.count()
        form.save()
        after_count = Student.objects.count()
        self.assertEqual(before_count + 1, after_count)

    # Test for allocated being boolean
    def test_allocated_is_boolean(self):
        # Valid values
        self.form_input['allocated'] = True
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        self.form_input['allocated'] = False
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())


