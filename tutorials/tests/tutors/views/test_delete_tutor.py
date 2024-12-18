from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Subject
from decimal import Decimal


class DeleteTutorTestCase(TestCase):
    def setUp(self):
        self.python_subject, created = Subject.objects.get_or_create(name = "Python")
        self.java_subject, created = Subject.objects.get_or_create(name = "Java")
        
        #Create User instances for testing
        self.user1 = User.objects.create_user(
            username="@janedoe",
            email="janedoe@example.com",
            password="password123",
            user_type="tutor"
        )
        self.client.login(username="@janedoe", password="password123")

        self.tutor = Tutor.objects.create(
            name="Jane Doe",
            username=self.user1,
            email="janedoe@gmail.com",
            rate = Decimal("25.50")
        )
        self.tutor.subjects.add(self.python_subject)
        self.tutor.subjects.add(self.java_subject)

        self.url = reverse('delete_tutor', kwargs={'tutor_id': self.tutor.id})
        self.invalid_url = reverse('delete_tutor', kwargs={'tutor_id': 999})

    def test_delete_tutor_url(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/delete/')

    def test_post_delete_tutor(self):
        self.client.login(username="@janedoe", password="password123")
        before_count = Tutor.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count - 1)
        with self.assertRaises(Tutor.DoesNotExist):
            Tutor.objects.get(id=self.tutor.id)

    def test_delete_tutor_does_not_exist(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_delete_tutor_get_confirmation_context(self):
        #log in the test client
        self.client.login(username="@janedoe", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected_message = 'Are you sure you want to delete the following tutor: &quot;Jane Doe&quot;.'
        self.assertIn(expected_message, response.content.decode())