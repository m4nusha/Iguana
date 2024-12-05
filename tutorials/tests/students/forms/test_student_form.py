from tutorials.models import User
from django.test import TestCase
from tutorials.forms import StudentForm
from tutorials.models import Student

class StudentFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="janedoe")  # Create a User instance
        self.form_input = {
            'name': "Doe, J.",
            'username': self.user,  # Use the User instance's ID for the ForeignKey
            'email': "janeDoe@gmail.com",  # Note the mixed case
            'allocated': False,  # Add allocated field if missing
            'payment': 'Pending'  # Add the payment status field
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
        self.assertIn('payment', form.fields)  # Ensure payment is a field


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
        self.form_input['username'] = None  # No User selected
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Test for unique username per Student
    def test_unique_username_per_student(self):
        Student.objects.create(
            name="Jane Smith",
            username=self.user,
            email="janesmith@gmail.com",
            allocated=True
        )
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

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
        new_user = User.objects.create(username="janedoe2", email="janedoe2@gmail.com")
        Student.objects.create(
            name="John Smith", username=new_user, email="janedoe@gmail.com", allocated=False
        )
        # Attempt to submit the form with the same email but different case
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Checkbox testing for allocated
    def test_checkbox_allocated_is_valid(self):
        form = StudentForm()
        self.assertIn('type="checkbox"', form.as_p())  # Check the HTML output contains a checkbox for allocated

    # Test for allocated being boolean
    def test_allocated_is_boolean(self):
        # Valid values
        self.form_input['allocated'] = True
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        self.form_input['allocated'] = False
        form = StudentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    # Test: Payment field
    def test_payment_field(self):
        # Valid payment status
        valid_payment = ['Pending', 'Successful']
        for status in valid_payment:
            self.form_input['payment'] = status
            form = StudentForm(data=self.form_input)
            self.assertTrue(form.is_valid())

        # Invalid payment status (should not be valid)
        self.form_input['payment'] = 'InvalidStatus'
        form = StudentForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        self.assertIn("Select a valid choice.", form.errors['payment'][0])  # Check for the exact error message

    # Save() function test case
    def test_valid_form_can_be_saved(self):
        form = StudentForm(data=self.form_input)
        before_count = Student.objects.count()
        form.save()
        after_count = Student.objects.count()
        self.assertEqual(before_count + 1, after_count)


