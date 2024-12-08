from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Subject

class TutorsViewTestCase(TestCase):
    def setUp(self):
        #create some sample tutors

        self.user1 = User.objects.create(username="johndoe")
        self.user2 = User.objects.create(username="janesmith")

        self.subject1 = Subject.objects.create(name = "Python")
        self.subject2 = Subject.objects.create(name = "Java")
        self.subject3 = Subject.objects.create(name = "Go")

        self.tutor1 = Tutor.objects.create(
            name="John Doe",
            username=self.user1,
            email="johndoe@example.com",
            rate=30.00
        )
        self.tutor1.subjects.add(self.subject1, self.subject2)

        self.tutor2 = Tutor.objects.create(
            name="Jane Smith",
            username=self.user2,
            email="janesmith@example.com",
            rate=26.75
        )
        self.tutor2.subjects.add(self.subject3)
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