from django.test import TestCase
from django.urls import reverse
from tutorials.models import Booking, User

class BookingsListTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="@johndoe", password="Password123", email="johndoe@gmail.com")
        self.user2 = User.objects.create_user(username="@janedoe", password="Password123", email="janedoe@gmail.com")
        self.booking1 = Booking.objects.create(student=self.user1, tutor=self.user2)
        self.booking2 = Booking.objects.create(student=self.user2, tutor=self.user1)
        self.url = reverse('booking_list')

    def test_bookings_url(self):
        """Test the correct URL for the bookings list"""
        self.assertEqual(self.url, '/bookings/')

    def test_get_bookings(self):
        """tests that the bookings list view returns the correct response"""
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_list.html')
        self.assertIn('bookings', response.context)
        bookings = response.context['bookings']
        self.assertEqual(bookings.count(), 2)

    def test_no_bookings(self):
        """tests if bookings list view returns the correct response when there's no bookings"""
        user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        Booking.objects.all().delete()
        response = self.client.get(reverse('booking_list'))
        self.assertContains(response, "<tr><td colspan='5' class='text-center'>No bookings available.</td></tr>", html=True)
