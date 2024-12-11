from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Booking, Student, Tutor

User = get_user_model()

class CreateBookingViewTest(TestCase):
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        self.url = reverse('booking_create')
        self.form_data = {'student': self.student.id, 'tutor': self.tutor.id, 'term': Booking.TERM1, 'lesson_type': Booking.TYPE_WEEKLY}

    def test_create_booking_url(self):
        """test the correct URL mapping for the create booking view"""
        self.assertEqual(self.url, '/bookings/create/')

    def test_get_create_booking_view(self):
        """test accessing the create booking view with a GET request"""
        self.client.login(username='student_user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_bound)

    def test_create_booking_redirects_when_not_logged_in(self):
        """test that an unauthenticated user is redirected to the login page"""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/log_in/?next={self.url}")

    def test_valid_post_creates_booking(self):
        """test a valid POST request successfully creates a booking"""
        self.client.login(username='student_user', password='password123')
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertRedirects(response, reverse('booking_list'))

    def test_invalid_post_does_not_create_booking(self):
        """test an invalid POST request does not create a booking"""
        self.client.login(username='student_user', password='password123')
        self.form_data['term'] = ''
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('term', response.context['form'].errors)

    def test_duplicate_booking_is_not_created(self):
        """test that attempting to create a duplicate booking is prevented"""
        self.client.login(username='student_user', password='password123')
        Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM1, lesson_type=Booking.TYPE_WEEKLY)
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('__all__', response.context['form'].errors)

    def test_create_booking_for_existing_booking_scenario(self):
        """test creating a booking where the student and tutor already have a similar booking"""
        self.client.login(username='student_user', password='password123')
        Booking.objects.create(student=self.student, tutor=self.tutor, term=Booking.TERM1, lesson_type=Booking.TYPE_WEEKLY)
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('__all__', response.context['form'].errors)

    def test_create_booking_redirects_on_success(self):
        """test that a successful booking creation redirects to the correct page"""
        self.client.login(username='student_user', password='password123')
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('booking_list'))

    def test_create_booking_with_invalid_student(self):
        """test that the booking cannot be created with a non-existing student"""
        self.client.login(username='student_user', password='password123')
        self.form_data['student'] = 9999
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('student', response.context['form'].errors)

    def test_create_booking_with_invalid_tutor(self):
        """test that the booking cannot be created with a non-existing tutor"""
        self.client.login(username='student_user', password='password123')
        self.form_data['tutor'] = 9999
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('tutor', response.context['form'].errors)

    def test_student_and_tutor_are_the_same(self):
        """test that the booking cannot be created if the student and tutor are the same"""
        self.client.login(username='student_user', password='password123')
        self.form_data['student'] = self.tutor.id
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_create.html')
        self.assertIn('__all__', response.context['form'].errors)
        self.assertIn('A student cannot book themselves as a tutor.', str(response.content))

    def test_create_booking_with_valid_student_and_tutor(self):
        """test that the booking is created successfully when student and tutor are valid and different"""
        self.client.login(username='student_user', password='password123')
        self.form_data['student'] = self.student.id
        self.form_data['tutor'] = self.tutor.id
        before_count = Booking.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertRedirects(response, reverse('booking_list'))
