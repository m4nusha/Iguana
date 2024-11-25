from django.test import TestCase
from django.urls import reverse
from tutorials.models import Booking, User

INVALID_BOOKING_ID = 0

class DeleteBookingViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.booking = Booking.objects.create(student=self.user, tutor=self.user)
        self.delete_url = reverse('booking_delete', kwargs={'pk': self.booking.id})
        self.booking_url = reverse('booking_show', kwargs={'booking_id': self.booking.id})
        self.booking_list_url = reverse('booking_list')

    def test_delete_booking_url(self):
        """test that the delete booking URL is correct"""
        self.assertEqual(self.delete_url, f'/bookings/delete/{self.booking.id}/')

    def test_get_delete_booking(self):
        """test that the GET request for a valid booking delete page works and renders the correct template"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_delete.html')

    def test_get_delete_booking_with_invalid_id(self):
        """test that a GET request with an invalid booking ID returns a 404 error"""
        invalid_url = reverse('booking_delete', kwargs={'pk': INVALID_BOOKING_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_delete_booking_with_valid_id(self):
        """test that a valid POST request deletes the booking and redirects"""
        self.client.login(username='testuser', password='12345')
        booking_id = self.booking.id
        before_count = Booking.objects.count()
        response = self.client.post(self.delete_url, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count - 1)
        expected_redirect_url = reverse('booking_list')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(pk=booking_id)

    def test_post_delete_booking_with_invalid_id(self):
        """test that attempting to delete a booking with an invalid ID returns a 404 error"""
        invalid_url = reverse('booking_delete', kwargs={'pk': INVALID_BOOKING_ID})
        before_count = Booking.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)

    def test_context_booking_in_delete_booking(self):
        """test that the booking being deleted is passed to the template context"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.delete_url)
        self.assertIn('booking', response.context)
        self.assertEqual(response.context['booking'].id, self.booking.id)

    def test_get_delete_booking_already_deleted(self):
        """test that accessing a deleted booking results in a 404 error"""
        self.booking.delete()
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 404)

    def test_booking_deleted_in_db(self):
        """test that the booking is actually deleted from the database"""
        booking_id = self.booking.id
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.delete_url, follow=True)
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(id=booking_id)
 
    def test_post_delete_booking(self):
        """test that the POST request deletes the booking"""
        self.client.login(username='testuser', password='12345')
        before_count = Booking.objects.count()
        response = self.client.post(self.delete_url, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count - 1)
        expected_redirect_url = reverse('booking_list')
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(pk=self.booking.id)

    def test_booking_cannot_be_accessed_after_deletion(self):
        """test that after deletion, the booking cannot be accessed"""
        booking_id = self.booking.id
        self.client.login(username='testuser', password='12345')
        self.client.post(self.delete_url, follow=True)
        response = self.client.get(reverse('booking_show', kwargs={'booking_id': booking_id}))
        self.assertEqual(response.status_code, 404)

