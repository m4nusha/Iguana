from django.test import TestCase
from django.urls import reverse
from tutorials.models import Booking, Session, User, Student, Tutor


class ShowBookingViewTest(TestCase):
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM1)
        
        self.session1 = Session.objects.create(booking=self.booking, session_date="2025-01-01", session_time="10:00:00")
        self.session2 = Session.objects.create(booking=self.booking, session_date="2025-01-02", session_time="11:00:00")
        
        self.url = reverse('session_list', kwargs={'booking_id': self.booking.id})

    def test_show_booking(self):
        """test that the booking and its sessions are displayed correctly"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.booking.lesson_type} Sessions for {self.student.username.get_full_name()} with {self.tutor.username.get_full_name()} ({self.booking.term})")
        self.assertContains(response, self.session1.session_date.strftime('%d/%m/%Y'))
        self.assertContains(response, self.session2.session_date.strftime('%d/%m/%Y'))

    def test_show_booking_404(self):
        """test that 404 is returned for a non-existing booking"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(reverse('session_list', kwargs={'booking_id': 99999}))
        self.assertEqual(response.status_code, 404)

    def test_show_booking_url(self):
        """test that the correct URL is generated for the booking show page"""
        self.url = reverse('session_list', kwargs={'booking_id': self.booking.id})
        self.assertEqual(self.url, f'/bookings/{self.booking.id}/sessions/')

    def test_show_booking_valid(self):
        """test that the booking and its sessions are displayed correctly"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_show.html')
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'].id, self.booking.id)
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0].id, self.session1.id)
        self.assertEqual(sessions[1].id, self.session2.id)

    def test_get_show_booking_invalid(self):
        """test that if the booking doesn't exist, a 404 error is raised"""
        self.client.login(username='student_user', password='password123')
        invalid_url = reverse('session_list', kwargs={'booking_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
    
    def test_context_variables(self):
        """test that the correct context variables are passed to the template"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertIn('booking', response.context)
        self.assertIn('sessions', response.context)
        self.assertEqual(response.context['booking'].term, self.booking.term)

    def test_session_urls(self):
        """test that the correct session URLs are generated for update and delete"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertContains(response, f'/sessions/update/{self.session1.id}/')
        self.assertContains(response, f'/sessions/delete/{self.session2.id}/')

    def test_show_booking_detail_view(self):
        """test that the booking detail view displays correctly"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_show.html')
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'].id, self.booking.id)

    def test_booking_detail_view_not_found(self):
        """test that a 404 is returned when accessing a non-existing booking"""
        self.client.login(username='student_user', password='password123')
        invalid_url = reverse('session_list', kwargs={'booking_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)