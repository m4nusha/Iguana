from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor,User,Subject
from decimal import Decimal
from tutorials.forms import TutorForm


INVALID_TUTOR_ID = 0

class UpdateTutorTestCase(TestCase):
    def setUp(self):
<<<<<<< HEAD
        # Create a User instance
        self.user = User.objects.create_user(
=======
        #Create Subject instances
        self.python_subject, created = Subject.objects.get_or_create(name="Python")
        self.java_subject, created = Subject.objects.get_or_create(name="Java")
        
        #Create unique User instances for testing
        self.user1 = User.objects.create_user(
>>>>>>> dd41c32 (test changes)
            username="@janedoe",
            email="janedoe@example.com",  #unique email
            password="password123",
            user_type="tutor"
        )
        self.user2 = User.objects.create_user(
            username="@johnsmith",
            email="johnsmith@example.com",  #unique email
            password="password123",
            user_type="tutor"
        )

        #Create the login user (@johndoe)
        self.login_user = User.objects.create_user(
            username="@johndoe",
            email="johndoe@example.com",  #unique email for login
            password="Password123",
            user_type="not specified"
        )
        self.client.login(username="@janedoe", password="password123")

        # Fetch the automatically created Tutor instance
        self.tutor1 = Tutor.objects.get(username=self.user1)

        # Update additional fields for the Tutor instance
        self.tutor1.name = "Jane Doe"
        self.tutor1.rate = Decimal("25.50")
        self.tutor1.subjects.add(self.python_subject)
        self.tutor1.subjects.add(self.java_subject)
        self.tutor1.save()


        # Fetch the automatically created Tutor instance
        self.tutor2 = Tutor.objects.get(username=self.user2)

        # Update additional fields for the Tutor instance
        self.tutor2.name = "John Smith"
        self.tutor2.rate = Decimal("28.00")
        self.tutor2.subjects.add(self.python_subject)
        self.tutor2.save()

        # Define the form_input dictionary for valid form data
        self.form_input = {
            'name': "Jane Updated",  # New name
            'username': self.user1.id,  # Use the user_id instead of username string
            'email': "updated@example.com",  # New email
            'rate': 35.00,  # Updated rate
            'subjects': [self.python_subject.id],  # Use subject IDs
        }


        self.url = reverse('update_tutor', kwargs={'tutor_id': self.tutor1.id})

    def test_update_tutor_url(self):
        #log in the test client
        self.client.login(username="@johndoe", password="Password123")
        self.assertEqual(self.url, f'/tutors/{self.tutor1.id}/edit/')

    def test_get_update_tutor(self):
        #log in the test client
        self.client.login(username="@johndoe", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutors/update_tutor.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, TutorForm))
        self.assertFalse(form.is_bound)

    def test_get_update_tutor_with_invalid_pk(self):
        #log in the test client
        self.client.login(username="@johndoe", password="Password123")
        """Test that trying to update a tutor with an invalid PK results in a 404."""
        invalid_url = reverse('update_tutor', kwargs={'tutor_id': INVALID_TUTOR_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)


    def test_post_with_valid_data(self):
        # Log in the test client
        self.client.login(username="@johndoe", password="Password123")
        
        tutor_id = self.tutor1.id
        before_count = Tutor.objects.count()

        # Perform POST request with valid form input
        response = self.client.post(self.url, self.form_input, follow=True)

        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count)  # Ensure no new tutor was created

<<<<<<< HEAD
        #verify redirection
        expected_redirect_url = reverse('tutors_list') 

        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
=======
        # Check for redirection and form errors (if any)
        if response.status_code == 302:
            expected_redirect_url = reverse('tutors_list')
            self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
>>>>>>> dd41c32 (test changes)

        # Verify updated tutor fields
        tutor = Tutor.objects.get(pk=tutor_id)
        self.assertEqual(self.form_input['name'], tutor.name)  # Verify name updated
        self.assertEqual(self.form_input['email'], tutor.email)  # Verify email updated
        self.assertEqual(self.form_input['rate'], tutor.rate)  # Verify rate updated

        # Verify subjects updated (make sure to compare subject IDs)
        updated_subjects = tutor.subjects.values_list('id', flat=True)
        self.assertEqual(list(self.form_input['subjects']), list(updated_subjects))  # Ensure subjects are updated


    def test_post_with_invalid_pk(self):
        #log in the test client
        self.client.login(username="@johndoe", password="Password123")
        """Test trying to update a tutor with an invalid PK."""
        invalid_url = reverse('update_tutor', kwargs={'tutor_id': INVALID_TUTOR_ID})
        before_count = Tutor.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count)  # No new tutor added
        self.assertEqual(response.status_code, 404)

    def test_post_with_invalid_data(self):
        #log in the test client
        self.client.login(username="@johndoe", password="Password123")
        """Test updating a tutor with invalid data."""
        self.form_input['name'] = ''  # Invalid form data (name is required)
        before_count = Tutor.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count)  # No new tutor added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutors/update_tutor.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, TutorForm))
        self.assertTrue(form.is_bound)
<<<<<<< HEAD

    def test_post_with_non_unique_email(self):
        """Test updating a tutor with a non-unique email address."""
        #create another User instance with a conflicting email
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        self.user1 = User.objects.create_user(
            username="@janesmith",
            email="janedoe.jr@example.com",  #conflicting email
            password="password123",
            user_type="not specified"
        )
        self.client.login(username="@johnsmith", password="password123")

        #create a Tutor instance for user1
        self.tutor1 = Tutor.objects.create(
            name="Jane Smith",
            username=self.user1,
            email="janedoe.jr@example.com",
            rate=35.00
        )

        before_count = Tutor.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tutor.objects.count()

        self.assertEqual(after_count, before_count)  #no new tutor should be added
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutors/update_tutor.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, TutorForm))
        self.assertTrue(form.is_bound)
        self.assertIn('email', form.errors)  #check if 'email' field has errors
=======
>>>>>>> dd41c32 (test changes)
