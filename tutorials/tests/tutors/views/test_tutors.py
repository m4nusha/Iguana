from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Subject
from decimal import Decimal

class TutorsViewTestCase(TestCase):
    def setUp(self):
        self.python_subject, created = Subject.objects.get_or_create(name = "Python")
        self.java_subject, created = Subject.objects.get_or_create(name = "Java")
        
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

        self.tutor1 = Tutor.objects.create(
            name="Jane Doe",
            username=self.user1,
            email="janedoe@example.com",
            rate = Decimal("25.50")
        )
        self.tutor2 = Tutor.objects.create(
            name="John Smith",
            username=self.user2,
            email="johnsmith@example.com",
            rate = Decimal("28.00")
        )


        self.tutor1.subjects.add(self.python_subject)
        self.tutor1.subjects.add(self.java_subject)
        self.tutor2.subjects.add(self.java_subject)
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
        self.assertEqual(tutors.count(), 2)  #ensure both tutors are in the context
        self.assertIn(self.tutor1, tutors)  #ensure tutor1 is in the context
        self.assertIn(self.tutor2, tutors)  #ensure tutor2 is in the context

        tutor_names = [tutor.name for tutor in tutors]
        self.assertIn(self.tutor1.name, tutor_names)
        self.assertIn(self.tutor2.name, tutor_names)

        #check that the tutors have the correct subjects
        tutor1_subjects = [subject.name for subject in self.tutor1.subjects.all()]
        tutor2_subjects = [subject.name for subject in self.tutor2.subjects.all()]
        self.assertIn("Python", tutor1_subjects)
        self.assertIn("Java", tutor1_subjects)
        self.assertIn("Java", tutor2_subjects)

    def test_no_tutors(self):
        """Ensure the tutors view handles an empty database gracefully."""
        Tutor.objects.all().delete()  #remove all tutors
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list_tutors.html')
        self.assertIn('tutors', response.context)
        tutors = response.context['tutors']
        self.assertEqual(tutors.count(), 0)  #no tutors should be in the context
        self.assertContains(response, "No tutors available")  #check the message is displayed