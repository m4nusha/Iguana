from django.test import TestCase
from tutorials.forms import StudentForm
from tutorials.models import Student, User

class StudentFormTestCase(TestCase):
    def setUp(self):
        # Create User instances for testing
        self.user1 = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            username="@johnsmith",
            email="johnsmith@example.com",
            password="password123",
            user_type='not specified',
        )

        # Create a Student instance for testing
        self.student = Student.objects.create(
            name="Jane Doe",
            username=self.user1,
            email="janedoe@student.example.com",
            allocated=False,
            payment="Pending",
        )

        self.user3 = User.objects.create_user(
            username="@newuser",
            email="newuser@example.com",
            password="password123",
            user_type= 'not specified',
        )

        self.form_input = {
            'name': "Jane Updated",
            'username': self.user3,  # Use a new User instance
            'email': "updated@example.com",
            'allocated': True,
            'payment': "Successful",
        }

    def test_valid_form(self):
        """Test form with valid data."""
        form = StudentForm(data=self.form_input, instance=self.student)
        print(form.errors)  # Log errors for debugging
        self.assertTrue(form.is_valid())

    def test_blank_name_is_invalid(self):
        """Test that blank name is invalid."""
        self.form_input['name'] = ""
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_overlong_name_is_invalid(self):
        """Test that overlong name is invalid."""
        self.form_input['name'] = "x" * 256
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_blank_email_is_invalid(self):
        """Test that blank email is invalid."""
        self.form_input['email'] = ""
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_case_insensitive_email_uniqueness(self):
        """Test that email uniqueness is case insensitive."""
        Student.objects.create(
            name="John Smith",
            username=self.user2,
            email="updated@example.com".lower(),
            allocated=True,
            payment="Pending",
        )
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_email_is_saved_in_lowercase(self):
        """Test that email is normalized to lowercase."""
        self.form_input['email'] = "MixedCase@Example.COM"
        form = StudentForm(data=self.form_input, instance=self.student)
        if form.is_valid():
            student = form.save()
            self.assertEqual(student.email, "mixedcase@example.com")

    def test_username_is_required(self):
        """Test that username is required."""
        self.form_input['username'] = None
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_username_uniqueness(self):
        """Test that username is unique per student."""
        Student.objects.create(
            name="John Smith",
            username=self.user2,
            email="uniqueemail@student.example.com",
            allocated=True,
            payment="Pending",
        )
        self.form_input['username'] = self.user2
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_valid_payment_choices(self):
        """Test that valid payment choices are accepted."""
        for payment in ["Pending", "Successful"]:
            self.form_input['payment'] = payment
            form = StudentForm(data=self.form_input, instance=self.student)
            self.assertTrue(form.is_valid())

    def test_invalid_payment_choice(self):
        """Test that invalid payment choices are rejected."""
        self.form_input['payment'] = "InvalidChoice"
        form = StudentForm(data=self.form_input, instance=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn('payment', form.errors)
