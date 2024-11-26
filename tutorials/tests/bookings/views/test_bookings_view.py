from django.test import TestCase
from django.urls import reverse
from tutorials.models import Booking, User

class BookingsListTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="password123", email="user1@example.com")
        self.user2 = User.objects.create_user(username="testuser2", password="password456", email="user2@example.com")
        self.booking1 = Booking.objects.create(student=self.user1, tutor=self.user2)
        self.booking2 = Booking.objects.create(student=self.user2, tutor=self.user1)
        self.url = reverse('booking_list')

    def test_bookings_url(self):
        """test the correct URL for the bookings list"""
        self.assertEqual(self.url, '/bookings/')

    def test_get_bookings(self):
        """test that the bookings list view returns the correct response"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_list.html')
        self.assertIn('bookings', response.context)
        bookings = response.context['bookings']
        self.assertEqual(bookings.count(), 2)

    def test_no_bookings(self):
        """test the response when no bookings are available"""
        Booking.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<table>")
        self.assertNotContains(response, "No bookings available.")
        self.assertEqual(response.context['bookings'].count(), 0)
