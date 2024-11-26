from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor
from tutorials.forms import TutorForm

class CreateTutorTestCase(TestCase):
    def setUp(self):
        self.url = reverse('create_tutor')
        self.form_input = {
            'name': "Doe, J.",
            'username': "janedoe",
            'email': "janedoe@gmail.com",
            'subject': "Math"
        }

    def test_create_tutor_url(self):
        self.assertEqual(self.url, '/tutors/create/')

    def test_get_create_tutor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_tutor.html')
        self.assertIn('form', response.context)

    def test_post_with_valid_data(self):
        before_count = Tutor.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count + 1)

    def test_post_with_invalid_data(self):
        self.form_input['email'] = ""
        before_count = Tutor.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'create_tutor.html')