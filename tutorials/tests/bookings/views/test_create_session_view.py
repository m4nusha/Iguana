from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Booking, Session, Student, Tutor

User = get_user_model()

class CreateSessionViewTest(TestCase):
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM1)
        self.url = reverse('session_create', args=[self.booking.id])
        self.form_data = {
            'session_date': '2025-01-01',
            'session_time': '10:00:00',
            'duration': '3600',
            'venue': 'Bush House',
            'payment_status': 'Pending',
        }

    def test_create_session_url(self):
        """test the correct URL mapping for the create session view"""
        self.assertEqual(self.url, f'/bookings/{self.booking.id}/sessions/create/')

    def test_get_create_session_view(self):
        """test accessing the create session view with a GET request"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/sessions/session_create.html')
        self.assertIn('form', response.context)
    
    def test_invalid_post_does_not_create_session(self):
        """test an invalid POST request does not create a session"""
        self.form_data['session_date'] = ''
        self.form_data['booking'] = self.booking.id
        before_count = Session.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/sessions/session_create.html')
        self.assertIn('session_date', response.context['form'].errors)
    
    def test_create_session_with_invalid_booking(self):
        """test that the session cannot be created with a non-existing booking"""
        invalid_url = reverse('session_create', args=[9999])
        before_count = Session.objects.count()
        response = self.client.post(invalid_url, data=self.form_data)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)

    # check!!
    def test_create_session_valid(self):
        """test a valid POST request to create a session"""
        before_count = Session.objects.count()
        self.form_data['booking'] = self.booking.id
        response = self.client.post(self.url, data=self.form_data)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('session_list', args=[self.booking.id]))

    def test_duplicate_session_is_not_created(self):
        """test that attempting to create a duplicate session is prevented"""
        session = Session.objects.create(
            booking=self.booking,
            session_date="2025-01-01",
            session_time="10:00:00",
            duration="3600",
            venue="Bush House",
            payment_status="Pending"
        )
        before_count = Session.objects.count()
        self.form_data['booking'] = self.booking.id
        response = self.client.post(self.url, data=self.form_data)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/sessions/session_create.html')
        self.assertIn('__all__', response.context['form'].errors)

    def test_session_duration_calculation(self):
        """test that the session duration is correctly calculated"""
        self.form_data['booking'] = self.booking.id
        session_data = self.form_data.copy()
        session_data['duration'] = str(3600)
        response = self.client.post(self.url, data=session_data)
        session = Session.objects.last()
        self.assertEqual(session.duration.total_seconds(), 3600)

    def test_create_session_with_no_payment_status(self):
        """test that a session cannot be created if no payment status is provided"""
        self.form_data['booking'] = self.booking.id
        form_data_no_payment_status = self.form_data.copy()
        form_data_no_payment_status['payment_status'] = ''
        before_count = Session.objects.count()
        response = self.client.post(self.url, data=form_data_no_payment_status)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertIn('payment_status', response.context['form'].errors)

    # check!!
    def test_create_session_redirects_on_success(self):
        """test that a successful session creation redirects to the correct page"""
        self.form_data['booking'] = self.booking.id
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('session_list', args=[self.booking.id]))