from django.forms import ValidationError
from django.test import TestCase
from tutorials.models import Booking, User
from tutorials.forms import UpdateBookingForm


class UpdateBookingModelTest(TestCase):
    """unit tests for updating a Booking model"""
    def setUp(self):
        """Set up initial data for tests."""
        self.student = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        self.tutor = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.booking = Booking.objects.create(term="Term1", student=self.student, tutor=self.tutor)
    
    def test_update_booking_with_valid_data(self):
        """successfully update booking with valid data"""
        self.booking.term = "UpdatedTerm"
        self.booking.save()
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertEqual(updated_booking.term, "UpdatedTerm")
        self.assertEqual(updated_booking.student, self.student)
        self.assertEqual(updated_booking.tutor, self.tutor)

    def test_update_booking_with_invalid_student(self):
        """prevent updating booking when student is invalid"""
        self.booking.student = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_update_booking_with_invalid_tutor(self):
        """prevent updating booking when tutor is invalid"""
        self.booking.tutor = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_update_booking_with_same_student_and_tutor(self):
        """prevent updating booking when student and tutor are the same"""
        self.booking.student = self.student
        self.booking.tutor = self.student
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_update_booking_with_invalid_term(self):
        """prevent updating booking with an invalid term"""
        self.booking.term = "InvalidTerm"
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_unique_constraint_on_updated_booking(self):
        """ensure duplicate bookings with the same term, student, and tutor cannot be updated"""
        student = User.objects.create_user(username='@student', password='password', email='student@example.com')
        tutor = User.objects.create_user(username='@tutor', password='password', email='tutor@example.com')
        booking = Booking.objects.create(term='Term1', student=student, tutor=tutor)
        booking2 = Booking.objects.create(term='Term1', student=student, tutor=tutor)
        booking2.term = 'Term1'
        with self.assertRaises(ValidationError):
            booking2.full_clean()

    def test_multiple_bookings_update(self):
        """ensure multiple bookings can be updated correctly for different terms"""
        booking1 = Booking.objects.create(term="Term1", student=self.student, tutor=self.tutor)
        booking2 = Booking.objects.create(term="Term2", student=self.student, tutor=self.tutor)
        booking1.term = "UpdatedTerm1"
        booking1.save()
        self.assertEqual(Booking.objects.filter(term="UpdatedTerm1").count(), 1)
        self.assertEqual(Booking.objects.filter(term="Term2").count(), 1)

    def test_update_booking_form_invalid_student(self):
        """ensure form rejects an invalid student"""
        form_data = {
            "term": "Term2", 
            "student": None,
            "tutor": self.tutor.id,
        }
        form = UpdateBookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("student", form.errors)

    def test_update_booking_form_invalid_tutor(self):
        """ensure form rejects an invalid tutor"""
        form_data = {
            "term": "Term2",
            "student": self.student.id,
            "tutor": None,
        }
        form = UpdateBookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("tutor", form.errors)

    def test_update_booking_form_with_same_student_and_tutor(self):
        """ensure form rejects booking with same student and tutor"""
        form_data = {
            "term": "Term2", 
            "student": self.student.id, 
            "tutor": self.student.id,
        }
        form = UpdateBookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("tutor", form.errors)
        self.assertEqual(form.errors["tutor"], ["The student and tutor cannot be the same person."])

    def test_update_booking_form_with_valid_data(self):
        """ensure form accepts valid data"""
        form_data = {
            "term": "Term3", 
            "student": self.student.id,
            "tutor": self.tutor.id,
        }
        form = UpdateBookingForm(data=form_data)
        self.assertTrue(form.is_valid())
