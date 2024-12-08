from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor,User,Subject

class UpdateTutorTestCase(TestCase):
    def setUp(self):

        self.user = User.objects.create(username = "janedoe")

        self.subject1 = Subject.objects.create(name="Python")
        self.subject2 = Subject.objects.create(name="Java")

        self.tutor = Tutor.objects.create(
            name="Doe, J.",
            username=self.user,
            email="janedoe@gmail.com",
            rate = 25.50
        )
        self.tutor.subjects.add(self.subject1)

        self.url = reverse('update_tutor', kwargs={'tutor_id': self.tutor.id})
        self.new_data = {
            'name': "John Doe",
            'username': self.user.username,
            'email': "johndoe@gmail.com",
            'rate': 30.00,
            'subjects': [self.subject2.id]
        }

    def test_update_tutor_url(self):
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/edit/')

    def test_get_update_tutor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_tutor.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertEqual(form.instance, self.tutor)

    def test_post_with_valid_data(self):
        """Test updating a tutor with valid data."""
        response = self.client.post(self.url, self.new_data, follow=True)
        self.assertEqual(response.status_code,200)
        self.tutor.refresh_from_db()
        self.assertEqual(self.tutor.name, self.new_data['name'])
        self.assertEqual(self.tutor.email, self.new_data['email'])
        self.assertEqual(self.tutor.rate, self.new_data['rate'])

        #verify the updated subjects
        updated_subjects = self.tutor.subjects.all()
        self.assertEqual(updated_subjects.count(), 1)  #only one subject now
        self.assertIn(self.subject2, updated_subjects) #check the subject has been updated correctly


    def test_post_with_invalid_data(self):
        """Test updating a tutor with invalid data."""
        invalid_data = self.new_data.copy()
        invalid_data['email'] = ""  #invalid email

        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 200)  #form redisplays with errors
        self.assertTemplateUsed(response, 'update_tutor.html')
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertFalse(form.is_valid())  #form should not be valid

        #ensure the tutor instance is not updated
        self.tutor.refresh_from_db()
        self.assertNotEqual(self.tutor.email, invalid_data['email'])