from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Booking, Student, Tutor

User = get_user_model()

class UpdateBookingViewTest(TestCase):
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM1, lesson_type=Booking.TYPE_WEEKLY)
        self.url = reverse('booking_update', kwargs={'pk': self.booking.id})
        self.form_data = {
            'student': self.student.id,
            'tutor': self.tutor.id,
            'term': Booking.TERM2,
            'lesson_type': Booking.TYPE_WEEKLY
        }

    def test_update_booking_url(self):
        """test the correct URL mapping for the update booking view"""
        self.assertEqual(self.url, f'/bookings/update/{self.booking.id}/')

    def test_get_update_booking_view(self):
        """test accessing the update booking view with a GET request"""
        self.client.login(username="student_user", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_update.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].instance.pk == self.booking.pk)

    def test_valid_post_updates_booking(self):
        """test a valid POST request successfully updates a booking"""
        self.client.login(username="student_user", password="password123")
        response = self.client.post(self.url, data=self.form_data, follow=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.term, Booking.TERM2)
        self.assertRedirects(response, reverse('booking_list'))

    def test_invalid_post_does_not_update_booking(self):
        """test an invalid POST request does not update a booking"""
        self.client.login(username="student_user", password="password123")
        self.form_data['term'] = ''
        before_term = self.booking.term
        response = self.client.post(self.url, data=self.form_data)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.term, before_term)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_update.html')
        self.assertIn('term', response.context['form'].errors)

    def test_update_booking_redirects_on_success(self):
        """test that a successful booking update redirects to the correct page"""
        self.client.login(username="student_user", password="password123")
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('booking_list'))

    def test_update_booking_for_invalid_booking(self):
        """test that trying to update a non-existent booking results in a 404 error"""
        self.client.login(username="student_user", password="password123")
        invalid_url = reverse('booking_update', kwargs={'pk': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)