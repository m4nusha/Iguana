from django.test import TestCase
from tutorials.forms import TutorForm
from tutorials.models import Tutor, User, Subject
from django.core.exceptions import ValidationError
from decimal import Decimal

class TutorFormTestCase(TestCase):
    def setUp(self):
        # self.subject1 = Subject.objects.create(name = "Python")
        # self.subject2 = Subject.objects.create(name = "Java")
        # self.form_input = {
        #     'name': "Doe, J.",
        #     'username': "janedoe",
        #     'email': "janedoe@gmail.com",
        #     'subjects': [self.subject1.id, self.subject2.id] #pass subject ids
        # }

        self.python_subject, created = Subject.objects.get_or_create(name = "Python")

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
        )

        # Create a Tutor instance for testing
        self.tutor = Tutor.objects.create(
            name="Jane Doe",
            username=self.user1,
            email="janedoe@student.example.com",
            rate = Decimal("30.00"),
        )
        self.tutor.subjects.add(self.python_subject)

        self.form_input = {
            'name': "Jane Updated",
            'username': self.user2,  #use a new User instance
            'email': "updated@example.com",
            'rate': Decimal("35.00"),
            'subjects': [self.python_subject],
        }
        self.form_input_valid = {
            'name': "Jane Doe",
            'username': self.user1,
            'email': "janedoe@example.com",
            'rate': Decimal("30.00"),
            'subjects': [self.python_subject],  #use a valid subject
        }
        #prepare invalid form data (using a non-existent subject ID)
        self.form_input_invalid = {
            'name': "John Smith",
            'username': self.user2,
            'email': "johnsmith@example.com",
            'rate': Decimal("30.00"),
            'subjects': [999],  #invalid subject ID
        }




    """Test cases"""
    def test_valid_form(self):
        form = TutorForm(data=self.form_input, instance=self.tutor)
        self.assertTrue(form.is_valid())
        tutor = form.save()
        self.assertTrue(tutor.subjects.filter(name="Python").exists())

    def test_default_subject_assigned(self):
        """Test that 'Python' is added as a default subject when no subjects are assigned."""
        self.form_input.pop('subjects')  #remove subjects from form input
        form = TutorForm(data=self.form_input, instance=self.tutor)
        self.assertTrue(form.is_valid())
        tutor = form.save()
        self.assertTrue(tutor.subjects.filter(name="Python").exists())

    def test_form_has_necessary_fields(self):
        form = TutorForm()
        self.assertIn('name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('subjects', form.fields)
        self.assertIn('rate', form.fields)

    def test_blank_name_is_invalid(self):
        """Test that a blank name is considered invalid"""
        self.form_input['name'] = ""
        form = TutorForm(data=self.form_input, instance = self.tutor)
        self.assertFalse(form.is_valid()),
        self.assertIn('name', form.errors, "The form should have an error for the 'name' field when it is blank.")

    # def test_blank_subject_is_valid(self):
    #     self.form_input['subjects'] = []   #no subjects selected
    #     form = TutorForm(data=self.form_input, instance = self.tutor)
    #     self.assertTrue(form.is_valid()),
    #     tutor = form.save()
    #     self.assertEqual(tutor.subjects.count(), 0, "The tutor should have no subjects assigned.")

    def test_blank_email_is_invalid(self):
        """Test that a blank email is considered invalid"""
        self.form_input['email'] = ""
        form = TutorForm(data=self.form_input, instance = self.tutor)
        self.assertFalse(form.is_valid()),
        self.assertIn('email', form.errors, "The form should have an error for the 'email' field when it is blank.")

    def test_duplicate_email_is_invalid(self):
        """Test that duplicate email addresses are invalid."""
        #create a tutor with the same email as in the form input
        Tutor.objects.create(
            name="John Smith",
            username=self.user2,
            email="janedoe@example.com",  #same email as in the form input
            rate=30.00,
        )
        self.form_input['email'] = "janedoe@example.com"
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid(), "The form should be invalid due to duplicate email.")
        self.assertIn('email', form.errors, "There should be an error for the email field.")


    def test_duplicate_username_is_invalid(self):
        """Test that duplicate usernames are invalid."""
        # Create a tutor with the same username as in the form input
        Tutor.objects.create(
            name="John Smith",
            username=self.user2,  # Same username as in the form input
            email="johnsmith@gmail.com",
            rate=Decimal("30.00"),
        )
        self.form_input['username'] = self.user2

        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid(), "The form should be invalid due to duplicate username.")
        self.assertIn('username', form.errors, "There should be an error for the username field.")


    
    def test_username_must_be_valid_user(self):
        """Tests that Username must be a valid User"""
        self.tutor.username = None  #setting username to None
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()


    # def test_valid_subject_choice(self):
    #     """Tests that valid subject choices are accepted"""
    #     form = TutorForm(data=self.form_input_valid)
    #     self.assertTrue(form.is_valid(), "The form should be valid with a valid subject.")

    def test_invalid_subject_choice(self):
        """Test that invalid subject choices are rejected."""
        form = TutorForm(data=self.form_input_invalid)
        self.assertFalse(form.is_valid(), "The form should be invalid when an invalid subject ID is selected.")
        self.assertIn('subjects', form.errors, "There should be an error for the 'subjects' field for invalid subject ID.")

    def test_valid_rate(self):
        """Test that valid rates are accepted."""
        for rate in [Decimal("36.00"), Decimal("45.50"), Decimal("19.99")]:
            self.form_input['rate'] = rate
            form = TutorForm(data=self.form_input)
            self.assertTrue(form.is_valid(), f"The form should be valid with a rate of {rate}.")

    def test_invalid_rate(self):
        """Test that invalid rates are rejected."""
        invalid_rates = [Decimal("-5.00"), Decimal("0.00"), Decimal("100000.00"), "not-a-number", None]

        for rate in invalid_rates:
            self.form_input['rate'] = rate
            form = TutorForm(data=self.form_input)
            self.assertFalse(form.is_valid(), f"The form should be invalid with a rate of {rate}.")
            self.assertIn('rate', form.errors, f"The rate field should have an error for rate: {rate}.")

    def test_case_insensitive_email_is_invalid(self):
        """Tests that email uniqueness is case-sensitive"""
        Tutor.objects.create(
            name = "John Smith",
            username = self.user2,
            email = "JohnSmith@Gmail.com",
            rate = Decimal("20.00")
        )
        #attempts to submit the form with the same email but different case
        form_data = {
            'name': "Duplicate Email",
            'username': self.user2,
            'email': "johnsmith@gmail.com",
            'rate': Decimal("20.00"),
            'subjects': [self.python_subject]
        }
        form = TutorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_default_rate_is_set(self):
        """Test that the default rate is set to 10.00 if not specified."""
        tutor_with_default_rate = Tutor.objects.create(
            name="John Smith",
            username=self.user2,
            email="johnsmith@gmail.com",
        )
        tutor_with_default_rate.subjects.add(self.python_subject)
        tutor_with_default_rate.save()
        self.assertEqual(tutor_with_default_rate.rate, 10.00)

    
    

    