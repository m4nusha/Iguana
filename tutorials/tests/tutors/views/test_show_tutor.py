from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Subject
from decimal import Decimal

class ShowTutorTestCase(TestCase):
    def setUp(self):
        self.python_subject, created = Subject.objects.get_or_create(name = "Python")
        self.java_subject, created = Subject.objects.get_or_create(name = "Java")
        
        # Create User instances for testing
        self.user1 = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
        )

        self.tutor = Tutor.objects.create(
            name="Jane Doe",
            username=self.user1,
            email="janedoe@gmail.com",
            rate = Decimal("25.50")
        )
        self.tutor.subjects.add(self.python_subject)
        self.tutor.subjects.add(self.java_subject)
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
        
        #ensure the tutor in the context is the same as the one created
        self.assertEqual(tutor.id, self.tutor.id)
        self.assertEqual(tutor.name, self.tutor.name)
        self.assertEqual(tutor.email, self.tutor.email)
        self.assertEqual(tutor.rate, self.tutor.rate)
        self.assertEqual(tutor.subjects.count(), 2)

        subject_names = [subject.name for subject in tutor.subjects.all()]
        self.assertIn("Python", subject_names)
        self.assertIn("Java", subject_names)


    def test_get_show_tutor_invalid(self):
        """Ensure an invalid tutor ID raises a 404 error."""
        invalid_url = reverse('show_tutor', kwargs={'tutor_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)