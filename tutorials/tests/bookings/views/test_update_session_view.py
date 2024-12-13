from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from tutorials.models import Session, Booking, Student, Tutor
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta

User = get_user_model()

class UpdateSessionViewTestCase(TestCase):
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        
        self.booking = Booking.objects.create(
            student=self.student, 
            tutor=self.tutor, 
            term='TERM1', 
            lesson_type='Weekly'
        )
        self.session = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(10, 0),
            duration=timedelta(hours=1),
            venue=Session.VENUE_BUSH_HOUSE,
            payment_status=Session.PAYMENT_PENDING
        )
        self.url = reverse('session_update', kwargs={'pk': self.session.pk})
        self.form_data = {
            'session_date': date(2025, 2, 1),
            'session_time': time(12, 0),
            'duration': timedelta(hours=1),
            'venue': Session.VENUE_WATERLOO,
            'payment_status': Session.PAYMENT_SUCCESSFUL
        }

    def test_get_update_session_view(self):
        """test accessing the session update view with a GET request"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sessions/session_update.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].instance.pk == self.session.pk)


    def test_post_update_session_view_invalid(self):
        """test submitting the form with invalid data (e.g., missing a required field)"""
        self.client.login(username='student_user', password='password123')
        invalid_data = self.form_data.copy()
        invalid_data['session_date'] = ''
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sessions/session_update.html')
        form_errors = response.context['form'].errors
        self.assertIn('session_date', form_errors)
    
    def test_redirect_if_not_logged_in(self):
        """Test that users who are not logged in are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/log_in/?next={self.url}")

    def test_access_denied_to_unauthorized_users(self):
        """Test that a user who is not associated with the session cannot update it."""
        other_user = User.objects.create_user(username="other_user", password="password123", email="other@example.com")
        self.client.login(username="other_user", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Assuming a 403 Forbidden response for unauthorized access

    def test_update_non_existent_session_returns_404(self):
        """Test accessing the update page for a non-existent session."""
        non_existent_url = reverse('session_update', kwargs={'pk': 9999})  # ID 9999 does not exist
        self.client.login(username='student_user', password='password123')
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_data_does_not_update_session(self):
        """Test that invalid form data does not update the session in the database."""
        self.client.login(username='student_user', password='password123')
        invalid_data = self.form_data.copy()
        invalid_data['session_time'] = 'invalid time'  # Invalid time format
        response = self.client.post(self.url, data=invalid_data)
        self.session.refresh_from_db()
        self.assertNotEqual(self.session.session_time, invalid_data['session_time'])  # Value shouldn't change
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sessions/session_update.html')


