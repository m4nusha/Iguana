from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Booking

User = get_user_model()

class UpdateBookingViewTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student", email="student@example.com", password="password")
        self.tutor = User.objects.create_user(username="tutor", email="tutor@example.com", password="password")
        self.booking = Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM1)
        self.url = reverse('booking_update', kwargs={'pk': self.booking.id})
        self.form_data = {
            'student': self.student.id,
            'tutor': self.tutor.id,
            'term': Booking.TERM2
        }

    def test_update_booking_url(self):
        """test the correct URL mapping for the update booking view"""
        self.assertEqual(self.url, f'/bookings/update/{self.booking.id}/')

    def test_get_update_booking_view(self):
        """test accessing the update booking view with a GET request"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_update.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].instance.pk == self.booking.pk)

    def test_valid_post_updates_booking(self):
        """test a valid POST request successfully updates a booking"""
        before_term = self.booking.term
        response = self.client.post(self.url, data=self.form_data, follow=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.term, Booking.TERM2)
        self.assertRedirects(response, reverse('booking_list'))

    def test_invalid_post_does_not_update_booking(self):
        """test an invalid POST request does not update a booking"""
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
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('booking_list'))

    def test_update_booking_for_duplicate_data(self):
        """test that trying to update a booking with duplicate data does not succeed"""
        Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM2)
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_update.html')
        self.assertIn('__all__', response.context['form'].errors)

    def test_update_booking_for_invalid_booking(self):
        """test that trying to update a non-existent booking results in a 404 error"""
        invalid_url = reverse('booking_update', kwargs={'pk': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
