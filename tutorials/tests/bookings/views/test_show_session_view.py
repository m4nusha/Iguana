from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Session, Tutor, Student, Booking
from datetime import timedelta

User = get_user_model()

class SessionShowViewTest(TestCase):
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term="Term1", lesson_type="Weekly")

        self.session = Session.objects.create(
            session_date="2025-01-01",
            session_time="10:00:00",
            duration=timedelta(seconds=3600),
            venue="Bush House",
            payment_status="Pending",
            booking=self.booking
        )
        self.url = reverse('session_show', args=[self.session.pk])

    def test_session_show_url(self):
        """Test correct URL mapping for the session_show view"""
        self.assertEqual(self.url, f'/sessions/{self.session.id}/')

    def test_get_session_show_view(self):
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sessions/session_show.html')
        self.assertIn('session', response.context)
        self.assertEqual(response.context['session'], self.session)

    def test_get_session_show_with_invalid_pk(self):
        self.client.login(username='student_user', password='password123')
        invalid_url = reverse('session_show', args=[9999])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_session_show_contains_session_data(self):
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertContains(response, "January 1, 2025")
        self.assertContains(response, self.session.session_time.strftime('%I:%M %p'))
        self.assertContains(response, self.session.venue)

    def test_session_show_redirect_for_non_existing_session(self):
        self.client.login(username='student_user', password='password123')
        invalid_session_id = 9999
        response = self.client.get(reverse('session_show', args=[invalid_session_id]))
        self.assertEqual(response.status_code, 404)