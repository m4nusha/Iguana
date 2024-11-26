from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor

class UpdateTutorTestCase(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(
            name="Doe, J.",
            username="janedoe",
            email="janedoe@gmail.com",
            subject="Math"
        )
        self.url = reverse('update_tutor', kwargs={'tutor_id': self.tutor.id})
        self.new_data = {
            'name': "John Doe",
            'username': "johndoe",
            'email': "johndoe@gmail.com",
            'subject': "Science"
        }

    def test_update_tutor_url(self):
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/edit/')

    def test_get_update_tutor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_tutor.html')

    def test_post_with_valid_data(self):
        response = self.client.post(self.url, self.new_data, follow=True)
        self.tutor.refresh_from_db()
        self.assertEqual(self.tutor.name, self.new_data['name'])
        self.assertEqual(self.tutor.email, self.new_data['email'])