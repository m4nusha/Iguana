from django.test import TestCase
from tutorials.forms import StudentForm
from tutorials.models import Student, User


class StudentFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="janedoe", email="janedoe@example.com")
        self.form_input = {
            'name': "Doe, J.",
            'username': self.user,  # Pass the User instance
            'email': "janeDoe@gmail.com",
            'allocated': False,
            'payment': 'Pending',
        }

    def test_valid_form(self):
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = StudentForm()
        self.assertIn('name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('allocated', form.fields)
        self.assertIn('payment', form.fields)

    def test_blank_name_is_invalid(self):
        self.form_input['name'] = ""
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overlong_name_is_invalid(self):
        self.form_input['name'] = 'x' * 256
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_username_is_invalid(self):
        self.form_input['username'] = None
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_unique_username_per_student(self):
        Student.objects.create(
            name="Jane Smith",
            username=self.user,
            email="janesmith@gmail.com",
            allocated=True,
        )
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_blank_email_is_invalid(self):
        self.form_input['email'] = ""
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overlong_email_is_invalid(self):
        self.form_input['email'] = "x" * 255 + "@example.com"
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_case_insensitive_email_is_invalid(self):
        new_user = User.objects.create(username="janedoe2", email="uniqueemail2@example.com")
        Student.objects.create(
            name="John Smith",
            username=new_user,
            email="janedoe@gmail.com",
            allocated=False,
        )
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_email_is_saved_in_lowercase(self):
        self.form_input['email'] = "MixedCase@Example.com"
        form = StudentForm(data=self.form_input)
        if form.is_valid():
            student = form.save()
            self.assertEqual(student.email, "mixedcase@example.com")

    def test_checkbox_allocated_is_valid(self):
        form = StudentForm()
        self.assertIn('type="checkbox"', form.as_p())

    def test_allocated_is_boolean(self):
        self.form_input['allocated'] = True
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        self.form_input['allocated'] = False
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_allocated_non_boolean_is_invalid(self):
        self.form_input['allocated'] = "NotABoolean"
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_payment_field(self):
        valid_payment = ['Pending', 'Successful']
        for status in valid_payment:
            self.form_input['payment'] = status
            form = StudentForm(data=self.form_input)
            self.assertTrue(form.is_valid())

        self.form_input['payment'] = 'InvalidStatus'
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_defaults_are_set_correctly(self):
        self.form_input.pop('allocated')
        self.form_input.pop('payment')
        form = StudentForm(data=self.form_input)
        if form.is_valid():
            student = form.save()
            self.assertFalse(student.allocated)
            self.assertEqual(student.payment, 'Pending')

    def test_update_student_email_uniqueness(self):
        student = Student.objects.create(
            name="Jane Doe",
            username=self.user,
            email="existing@example.com",
            allocated=False,
        )
        form_input = {
            'name': "Jane Updated",
            'username': self.user,
            'email': "existing@example.com",
            'allocated': False,
            'payment': 'Pending',
        }
        form = StudentForm(data=form_input, instance=student)
        self.assertTrue(form.is_valid())

    def test_valid_form_can_be_saved(self):
        form = StudentForm(data=self.form_input)
        before_count = Student.objects.count()
        if form.is_valid():
            form.save()
        after_count = Student.objects.count()
        self.assertEqual(before_count + 1, after_count)
