from django.test import TestCase
from django.urls import reverse
from tutorials.models import Booking, Session, User


class ShowBookingViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.booking = Booking.objects.create(student=self.user, tutor=self.user)
        self.session1 = Session.objects.create(booking=self.booking, session_date="2025-01-01", session_time="10:00:00")
        self.session2 = Session.objects.create(booking=self.booking, session_date="2025-01-02", session_time="11:00:00")
        self.url = reverse('booking_show', kwargs={'booking_id': self.booking.id})

    def test_show_booking(self):
        """test that the booking and its sessions are displayed correctly"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('booking_show', kwargs={'booking_id': self.booking.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Sessions for {self.booking.student.full_name} with {self.booking.tutor.full_name} ({self.booking.term})")
        self.assertContains(response, self.session1.session_date.strftime('%d/%m/%Y'))
        self.assertContains(response, self.session2.session_date.strftime('%d/%m/%Y'))

    def test_show_booking_404(self):
        """test that 404 is returned for a non-existing booking"""
        response = self.client.get(reverse('booking_show', kwargs={'booking_id': 99999}))
        self.assertEqual(response.status_code, 404)

    def test_show_booking_url(self):
        """test that the correct URL is generated for the booking show page"""
        self.url = reverse('session_list', kwargs={'booking_id': self.booking.id})
        self.assertEqual(self.url, f'/bookings/{self.booking.id}/sessions/')

    def test_show_booking_valid(self):
        """test that the booking and its sessions are displayed correctly"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myTests/booking_show.html')
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'].id, self.booking.id)
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0].id, self.session1.id)
        self.assertEqual(sessions[1].id, self.session2.id)

    def test_get_show_booking_invalid(self):
        """test that if the booking doesn't exist, a 404 error is raised"""
        invalid_url = reverse('booking_show', kwargs={'booking_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
    
    def test_context_variables(self):
        """test that the correct context variables are passed to the template"""
        response = self.client.get(self.url)
        self.assertIn('booking', response.context)
        self.assertIn('sessions', response.context)
        self.assertEqual(response.context['booking'].term, self.booking.term)

    def test_session_urls(self):
        """test that the correct session URLs are generated for update and delete"""
        response = self.client.get(self.url)
        self.assertContains(response, f'/sessions/update/{self.session1.id}/')
        self.assertContains(response, f'/sessions/delete/{self.session2.id}/')

