from django.test import TestCase
from django.core.exceptions import ValidationError
from tutorials.forms import BookingForm
from tutorials.models import Student, Tutor, User, Booking

class CreateBookingFormTest(TestCase):
    """unit tests for creating a booking with the BookingForm"""
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        self.valid_data = {"term": "Term1", "lesson_type": "Weekly", "student": self.student.id, "tutor": self.tutor.id,}

    def test_form_fields(self):
        """form contains required fields and accepts valid data"""
        form = BookingForm(data=self.valid_data)
        required_fields = ['term', 'lesson_type', 'student', 'tutor']
        for field in required_fields:
            self.assertIn(field, form.fields)
        self.assertTrue(form.is_valid())

    def test_booking_creation(self):
        """creating a booking with valid data"""
        form = BookingForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        booking = form.save()
        self.assertEqual(booking.term, self.valid_data["term"])
        self.assertEqual(booking.lesson_type, self.valid_data["lesson_type"])
        self.assertEqual(booking.student, self.student)
        self.assertEqual(booking.tutor, self.tutor)

    def test_form_invalid_missing_term(self):
        """form should be invalid if 'term' is missing"""
        invalid_data = self.valid_data.copy()
        invalid_data["term"] = ""
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)

    def test_form_invalid_missing_lesson_type(self):
        """form should be invalid if 'lesson_type' is missing"""
        invalid_data = self.valid_data.copy()
        invalid_data["lesson_type"] = ""
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('lesson_type', form.errors)

    def test_form_invalid_missing_student(self):
        """form should be invalid if 'student' is missing"""
        invalid_data = self.valid_data.copy()
        invalid_data["student"] = None
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('student', form.errors)

    def test_form_invalid_missing_tutor(self):
        """form should be invalid if 'tutor' is missing"""
        invalid_data = self.valid_data.copy()
        invalid_data["tutor"] = None
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor', form.errors)

    def test_form_missing_fields(self):
        """form should be invalid if required fields are missing"""
        form = BookingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)
        self.assertIn('lesson_type', form.errors)
        self.assertIn('student', form.errors)
        self.assertIn('tutor', form.errors)

    def test_form_invalid_nonexistent_student(self):
        """form should be invalid if student does not exist"""
        invalid_data = self.valid_data.copy()
        invalid_data["student"] = 999
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('student', form.errors)

    def test_form_invalid_nonexistent_tutor(self):
        """form should be invalid if tutor does not exist"""
        invalid_data = self.valid_data.copy()
        invalid_data["tutor"] = 999
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor', form.errors)

    def test_form_invalid_duplicate_booking(self):
        """form should be invalid if a duplicate booking exists"""
        Booking.objects.create(term=self.valid_data["term"], lesson_type=self.valid_data["lesson_type"], student=self.student, tutor=self.tutor)
        form = BookingForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValidationError):
            form.clean()

    def test_form_invalid_term_choice(self):
        """form should be invalid if 'term' has an invalid choice"""
        invalid_data = self.valid_data.copy()
        invalid_data["term"] = "InvalidTerm"
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('term', form.errors)

    def test_form_invalid_lesson_type_choice(self):
        """form should be invalid if 'lesson_type' has an invalid choice"""
        invalid_data = self.valid_data.copy()
        invalid_data["lesson_type"] = "InvalidLessonType"
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('lesson_type', form.errors)
    
    def test_form_increases_booking_count(self):
        """creating a valid booking should increase Booking count"""
        initial_count = Booking.objects.count()
        form = BookingForm(data=self.valid_data)
        if form.is_valid():
            form.save()
        final_count = Booking.objects.count()
        self.assertEqual(final_count, initial_count + 1, "booking count did not increase after creating a new Booking.")

    def test_form_invalid_nonunique_combination(self):
        """form should use unique_together constraint"""
        Booking.objects.create(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        form = BookingForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValidationError):
            form.clean()

    def test_form_invalid_deleted_student(self):
        """form should be invalid if the student is deleted"""
        self.student.delete()
        invalid_data = self.valid_data.copy()
        invalid_data["student"] = self.student.id
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('student', form.errors)

    def test_form_invalid_deleted_tutor(self):
        """form should be invalid if the tutor is deleted"""
        self.tutor.delete()
        invalid_data = self.valid_data.copy()
        invalid_data["tutor"] = self.tutor.id
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor', form.errors)
