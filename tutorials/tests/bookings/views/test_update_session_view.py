from django.test import TestCase
from django.urls import reverse
from tutorials.models import Session, Booking
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta

User = get_user_model()

class UpdateSessionViewTestCase(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student", email="student@example.com", password="password")
        self.tutor = User.objects.create_user(username="tutor", email="tutor@example.com", password="password")
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term='TERM1')
        self.session = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(10, 0),
            duration=timedelta(hours=1),
            lesson_type=Session.TYPE_WEEKLY,
            venue=Session.VENUE_BUSH_HOUSE,
            amount=100.00,
            payment_status=Session.PAYMENT_PENDING
        )
        self.url = reverse('session_update', kwargs={'pk': self.session.pk})
        self.form_data = {
            'session_date': date(2025, 2, 1),
            'session_time': time(12, 0),
            'duration': timedelta(hours=1),
            'lesson_type': Session.TYPE_FORTNIGHT,
            'venue': Session.VENUE_WATERLOO,
            'amount': 120.00,
            'payment_status': Session.PAYMENT_SUCCESSFUL
        }

    def test_get_update_session_view(self):
        """test accessing the session update view with a GET request"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/sessions/session_update.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].instance.pk == self.session.pk)

    def test_post_update_session_view_valid(self):
        """test submitting the form with valid data"""
        response = self.client.post(self.url, data=self.form_data)
        self.session.refresh_from_db()
        self.assertEqual(self.session.session_date, self.form_data['session_date'])
        self.assertEqual(self.session.session_time, self.form_data['session_time'])
        self.assertEqual(self.session.lesson_type, self.form_data['lesson_type'])
        self.assertEqual(self.session.venue, self.form_data['venue'])
        self.assertEqual(self.session.amount, self.form_data['amount'])
        self.assertEqual(self.session.payment_status, self.form_data['payment_status'])
        self.assertRedirects(response, reverse('session_list', kwargs={'booking_id': self.booking.pk}))

    def test_post_update_session_view_invalid(self):
        """test submitting the form with invalid data (e.g., missing a required field)"""
        invalid_data = self.form_data.copy()
        invalid_data['session_date'] = ''
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/sessions/session_update.html')
        form_errors = response.context['form'].errors
        self.assertIn('session_date', form_errors)

    def test_update_session_redirects_on_success(self):
        """test that a successful session update redirects to the correct page"""
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('session_list', kwargs={'booking_id': self.booking.pk}))