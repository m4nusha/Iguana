from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Subject

class ShowTutorTestCase(TestCase):
    def setUp(self):
        # Create a sample tutor
        self.user = User.objects.create(username = "janedoe")

        self.subject1 = Subject.objects.create(name = "Python")
        self.subject2 = Subject.objects.create(name = "Java")

        self.tutor = Tutor.objects.create(
            name="John Doe",
            username="johndoe",
            email="johndoe@example.com",
            rate = 25.50
        )
        self.tutor.subjects.add(self.subject1, self.subject2)   #add subjects
        self.url = reverse('show_tutor', kwargs={'tutor_id': self.tutor.id})

    def test_show_tutor_url(self):
        """Ensure the URL for show_tutor resolves correctly."""
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/')

    def test_get_show_tutor_valid(self):
        """Ensure a valid tutor ID returns the correct response and context."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_tutor.html')
        self.assertIn('tutor', response.context)
        tutor = response.context['tutor']
        self.assertEqual(tutor.id, self.tutor.id)
        self.assertEqual(tutor.name, self.tutor.name)

    def test_get_show_tutor_invalid(self):
        """Ensure an invalid tutor ID raises a 404 error."""
        invalid_url = reverse('show_tutor', kwargs={'tutor_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)