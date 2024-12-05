from django.test import TestCase
from django.urls import reverse
from tutorials.models import Booking, Session, User

INVALID_SESSION_ID = 0

class DeleteSessionViewTest(TestCase):
    def setUp(self):
        self.student = User.objects.create(username="johndoe",first_name="John",last_name="Doe",email="johndoe@example.com")
        self.tutor = User.objects.create(username="janesmith",first_name="Jane",last_name="Smith",email="janesmith@example.com")
        self.booking = Booking.objects.create(student=self.student,tutor=self.tutor,term="TERM1", lesson_type="WEEKLY")
        self.session = Session.objects.create(
            booking=self.booking,
            session_date="2025-01-01",
            session_time="10:00:00",
            duration="01:00:00",
            venue=Session.VENUE_BUSH_HOUSE,
            payment_status=Session.PAYMENT_PENDING
        )
        self.url = reverse('session_delete', kwargs={'pk': self.session.id})

    def test_delete_session_url(self):
        """test the URL for deleting a session is correct"""
        self.assertEqual(self.url, f'/sessions/delete/{self.session.id}/')

    def test_get_delete_session(self):
        """test the GET request to the session delete page works and renders the correct template"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/sessions/session_delete.html')

    def test_get_delete_session_with_invalid_pk(self):
        """test that an invalid session ID results in a 404 error"""
        invalid_url = reverse('session_delete', kwargs={'pk': INVALID_SESSION_ID})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_post_with_valid_id(self):
        """test that posting to the delete session page with a valid session ID deletes the session"""
        session_id = self.session.id
        before_count = Session.objects.count()
        response = self.client.post(self.url, follow=True)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count - 1)
        expected_redirect_url = reverse('session_list', kwargs={'booking_id': self.booking.id})
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)
        with self.assertRaises(Session.DoesNotExist):
            Session.objects.get(pk=session_id)

    def test_post_with_invalid_pk(self):
        """test that posting to delete a session with an invalid ID does not delete anything"""
        invalid_url = reverse('session_delete', kwargs={'pk': INVALID_SESSION_ID})
        before_count = Session.objects.count()
        response = self.client.post(invalid_url, follow=True)
        after_count = Session.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 404)

    def test_delete_session_with_deleted_booking(self):
        """test that trying to delete a session with a deleted booking results in a 404 error"""
        self.client.login(username='testuser', password='12345')
        self.booking.delete()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_session_deletion_related_booking_not_deleted(self):
        """test that deleting a session doesn't delete the related booking"""
        before_booking_count = Booking.objects.count()
        before_session_count = Session.objects.count()
        self.client.post(self.url, follow=True)
        self.assertEqual(Booking.objects.count(), before_booking_count)
        self.assertEqual(Session.objects.count(), before_session_count - 1)

    def test_session_deleted_in_db(self):
        """test that the session is actually deleted from the database"""
        session_id = self.session.id
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.url, follow=True)
        with self.assertRaises(Session.DoesNotExist):
            Session.objects.get(id=session_id)

    def test_redirect_after_session_deletion(self):
        """test that after deleting a session, the user is redirected to the correct page"""
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.url, follow=True)
        expected_redirect_url = reverse('session_list', kwargs={'booking_id': self.booking.id})
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

    def test_session_cannot_be_accessed_after_deletion(self):
        """test that after deletion, the session cannot be accessed"""
        session_id = self.session.id
        self.client.login(username='testuser', password='12345')
        self.client.post(self.url, follow=True)
        response = self.client.get(reverse('session_show', kwargs={'pk': session_id}))
        self.assertEqual(response.status_code, 404)