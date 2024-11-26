from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor

class TutorsViewTestCase(TestCase):
    def setUp(self):
        # Create some sample tutors
        self.tutor1 = Tutor.objects.create(
            name="John Doe",
            username="johndoe",
            email="johndoe@example.com",
            subject="Math"
        )
        self.tutor2 = Tutor.objects.create(
            name="Jane Smith",
            username="janesmith",
            email="janesmith@example.com",
            subject="Physics"
        )
        self.url = reverse('tutors')  # URL for the tutors view

    def test_tutors_url(self):
        """Ensure the URL for the tutors view resolves correctly."""
        self.assertEqual(self.url, '/tutors/')

    def test_get_tutors_view(self):
        """Ensure the tutors view returns the correct response and context."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_tutors.html')
        self.assertIn('tutors', response.context)
        tutors = response.context['tutors']
        self.assertEqual(tutors.count(), 2)  # Ensure both tutors are in the context
        self.assertIn(self.tutor1, tutors)  # Ensure tutor1 is in the context
        self.assertIn(self.tutor2, tutors)  # Ensure tutor2 is in the context

    def test_no_tutors(self):
        """Ensure the tutors view handles an empty database gracefully."""
        Tutor.objects.all().delete()  # Remove all tutors
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_tutors.html')
        self.assertIn('tutors', response.context)
        tutors = response.context['tutors']
        self.assertEqual(tutors.count(), 0)  # No tutors should be in the context
        self.assertContains(response, "No tutors available")  # Check the message is displayed