from django.forms import ValidationError
from django.test import TestCase
from tutorials.models import Booking, User


class CreateBookingModelTest(TestCase):
    """unit tests for the Booking model"""
    def setUp(self):
        self.student = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        self.tutor = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")

    def test_create_booking_with_valid_data(self):
        """successfully create a booking with valid data"""
        booking = Booking.objects.create(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        self.assertIsInstance(booking, Booking)
        self.assertEqual(booking.term, "Term1")
        self.assertEqual(booking.lesson_type, "Weekly")
        self.assertEqual(booking.student, self.student)
        self.assertEqual(booking.tutor, self.tutor)

    def test_booking_with_same_student_and_tutor(self):
        """prevent booking when student and tutor are the same"""
        booking = Booking(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.student)
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_unique_constraint_on_booking(self):
        """ensure duplicate bookings with same term, student and tutor are not allowed"""
        student = User.objects.create_user(username='@student', password='password', email='student@example.com')
        tutor = User.objects.create_user(username='@tutor', password='password', email='tutor@example.com')
        booking = Booking.objects.create(term='Term1', student=student, tutor=tutor)
        self.assertEqual(str(booking), f'Term1 | Student: {student.full_name} | Tutor: {tutor.full_name}')
        with self.assertRaises(ValidationError):
            booking2 = Booking(term='Term1', student=student, tutor=tutor)
            booking2.full_clean()
    
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

