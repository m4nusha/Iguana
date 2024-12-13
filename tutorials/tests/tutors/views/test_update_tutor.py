from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor,User,Subject
from decimal import Decimal
from tutorials.forms import TutorForm


INVALID_TUTOR_ID = 0

class UpdateTutorTestCase(TestCase):
    def setUp(self):
        # Create a User instance
        self.user = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
            user_type="not specified"
        )
        self.client.login(username="@janedoe", password="password123")

        #create a Tutor instance referencing the User instance
        self.tutor = Tutor.objects.create(
            name="Jane Doe",
            username=self.user,
            email="janedoe@example.com",
            rate = Decimal("15.00")
        )
        self.subject, created = Subject.objects.get_or_create(name="Python")
        self.tutor.subjects.add(self.subject)

        self.form_input = {
            'name': "Jane Doe Jr.",
            'username':  self.user, #new username for update
            'email': "Jane.doe.jr@example.com",
            'rate': Decimal("20.00"),
            'subjects': [self.subject.id],
        }

        #URL for the show_tutor view
        self.url = reverse('update_tutor', kwargs={'tutor_id': self.tutor.id})

    def test_update_tutor_url(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/edit/')

    def test_get_update_tutor(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutors/update_tutor.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertTrue(isinstance(form, TutorForm))
        self.assertFalse(form.is_bound)

    def test_get_update_tutor_with_invalid_pk(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        """Test that trying to update a tutor with an invalid PK results in a 404."""
        invalid_url = reverse('update_tutor', kwargs={'tutor_id': INVALID_TUTOR_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_data(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        tutor_id = self.tutor.id
        before_count = Tutor.objects.count()

        #perform POST request with valid form input
        response = self.client.post(self.url, self.form_input, follow=True)

        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count)  #ensure no new tutor was created

        #verify redirection
        expected_redirect_url = reverse('tutors_list') 

        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

        #verify updated student fields
        tutor = Tutor.objects.get(pk=tutor_id)
        self.assertEqual(self.form_input['name'], tutor.name)
        self.assertEqual(self.form_input['username'], tutor.username)  #correctly compare User instance
        self.assertEqual(self.form_input['email'], tutor.email)
        self.assertEqual(self.form_input['rate'], tutor.rate)
        self.assertEqual(self.form_input['subjects'], list(tutor.subjects.values_list('id', flat=True)))


    def test_post_with_invalid_pk(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        """Test trying to update a tutor with an invalid PK."""
        invalid_url = reverse('update_tutor', kwargs={'tutor_id': INVALID_TUTOR_ID})
        before_count = Tutor.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count)  # No new tutor added
        self.assertEqual(response.status_code, 404)

    def test_post_with_invalid_data(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
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