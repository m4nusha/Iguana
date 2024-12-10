from django.forms import ValidationError
from django.test import TestCase
from tutorials.models import Booking, Student, Tutor, User


class CreateBookingModelTest(TestCase):
    """unit tests for the Booking model"""
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)

    def test_create_booking_with_valid_data(self):
        """successfully create a booking with valid data"""
        booking = Booking.objects.create(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        self.assertIsInstance(booking, Booking)
        self.assertEqual(booking.term, "Term1")
        self.assertEqual(booking.lesson_type, "Weekly")
        self.assertEqual(booking.student, self.student)
        self.assertEqual(booking.tutor, self.tutor)
    
    def test_multiple_bookings(self):
        """ensure multiple bookings can be created for different terms with same student and tutor"""
        Booking.objects.create(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        Booking.objects.create(term="Term2", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        self.assertEqual(Booking.objects.count(), 2)

    def test_update_booking_to_duplicate_another(self):
        """Ensure updating a booking to duplicate another is invalid."""
        Booking.objects.create(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        another_booking = Booking.objects.create(term="Term2", lesson_type="Fortnight", student=self.student, tutor=self.tutor)
        another_booking.term = "Term1"
        another_booking.lesson_type = "Weekly"
        with self.assertRaises(ValidationError):
            another_booking.full_clean()
    
    def test_nonexistent_student_or_tutor(self):
        """ensure validation fails for non-existent student or tutor"""
        non_existing_user_id = 9999
        with self.assertRaises(ValidationError):
            booking = Booking(term="Term1", lesson_type="Weekly", student_id=non_existing_user_id, tutor=self.tutor)
            booking.full_clean()