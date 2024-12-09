from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Session, Booking
from datetime import timedelta, date, time


class SessionsListTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.student = User.objects.create_user(username='student', email='student@example.com', password='Password123')
        self.tutor = User.objects.create_user(username='tutor', email='tutor@example.com', password='Password123')
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term="TERM1")
        self.session1 = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(10, 0),
            duration=timedelta(hours=1),
            venue=Session.VENUE_BUSH_HOUSE,
            payment_status=Session.PAYMENT_PENDING
        )
        self.session2 = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 2),
            session_time=time(14, 0),
            duration=timedelta(hours=1),
            venue=Session.VENUE_WATERLOO,
            payment_status=Session.PAYMENT_SUCCESSFUL
        )
        self.url = reverse('session_list', kwargs={'booking_id': self.booking.id})
        
    def test_sessions_url(self):
        self.assertEqual(self.url, f'/bookings/{self.booking.id}/sessions/')
        
    # check!!
    def test_get_sessions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_show.html')
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(sessions.count(), 2)
    
    def test_no_sessions(self):
        """test the response when no sessions are available"""
        self.booking.sessions.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No sessions available.")
        self.assertEqual(response.context['sessions'].count(), 0)
