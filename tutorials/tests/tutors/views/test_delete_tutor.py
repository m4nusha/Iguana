from django.test import TestCase
from django.urls import reverse
from tutorials.models import Tutor, User, Subject

class DeleteTutorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="janedoe")

        self.subject1 = Subject.objects.create(name = "Python")
        self.subject2 = Subject.objects.create(name = "Java")

        self.tutor = Tutor.objects.create(
            name="Doe, J.",
            username="janedoe",
            email="janedoe@gmail.com",
            rate = 25.50
        )
        self.tutor.subjects.add(self.subject1, self.subject2)
        self.url = reverse('delete_tutor', kwargs={'tutor_id': self.tutor.id})

    def test_delete_tutor_url(self):
        self.assertEqual(self.url, f'/tutors/{self.tutor.id}/delete/')

    def test_post_delete_tutor(self):
        before_count = Tutor.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count - 1)