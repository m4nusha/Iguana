from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Session, Booking, Tutor, Student
from datetime import timedelta, date, time


class SessionsListTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user(username="@johndoe", password="Password123", email="johndoe@gmail.com")
        self.user2 = User.objects.create_user(username="@janedoe", password="Password123", email="janedoe@gmail.com")
        
        self.student1 = Student.objects.create(username=self.user1, email="johndoe_unique@gmail.com", name=self.user1.get_full_name())
        self.student2 = Student.objects.create(username=self.user2, email="janedoe_unique@gmail.com", name=self.user2.get_full_name())
        self.tutor1 = Tutor.objects.create(username=self.user2, email=self.user2.email, name=self.user2.get_full_name())
        self.tutor2 = Tutor.objects.create(username=self.user1, email=self.user1.email, name=self.user1.get_full_name())
        
        self.booking1 = Booking.objects.create(student=self.student1, tutor=self.tutor2)
        self.booking2 = Booking.objects.create(student=self.student2, tutor=self.tutor1)

        self.session1 = Session.objects.create(
            booking=self.booking1,
            session_date=date(2025, 1, 1),
            session_time=time(10, 0),
            duration=timedelta(hours=1),
            venue=Session.VENUE_BUSH_HOUSE,
            payment_status=Session.PAYMENT_PENDING
        )
        self.session2 = Session.objects.create(
            booking=self.booking1,
            session_date=date(2025, 1, 2),
            session_time=time(14, 0),
            duration=timedelta(hours=1),
            venue=Session.VENUE_WATERLOO,
            payment_status=Session.PAYMENT_SUCCESSFUL
        )
        self.url = reverse('session_list', kwargs={'booking_id': self.booking1.id})

    def test_sessions_url(self):
        """test the correct URL for the session list"""
        self.assertEqual(self.url, f'/bookings/{self.booking1.id}/sessions/')
        
    def test_get_sessions(self):
        """test that the GET request for the session list page returns the correct response"""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_show.html')
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(sessions.count(), 2)
    
    def test_no_sessions(self):
        """test that the session list view behaves correctly when no sessions exist"""
        self.booking1.sessions.all().delete()
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="alert alert-info">No sessions available.</div>', html=True)
        self.assertEqual(response.context['sessions'].count(), 0)