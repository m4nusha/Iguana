from django.forms import ValidationError
from django.test import TestCase
from tutorials.forms import UpdateBookingForm
from tutorials.models import Booking, Student, Tutor, User

class UpdateBookingFormTestCase(TestCase):
    """unit tests for the UpdateBookingForm"""
    
    def setUp(self):
        student_user = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        tutor_user = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.student = Student.objects.create(username=student_user)
        self.tutor = Tutor.objects.create(username=tutor_user)
        self.existing_booking = Booking.objects.create(term="Term1", lesson_type="Weekly", student=self.student, tutor=self.tutor)
        self.valid_data = {"term": "Term2", "lesson_type": "Weekly", "student": self.student.id, "tutor": self.tutor.id,}

    def test_form_contains_required_fields(self):
        """form contains required fields"""
        form = UpdateBookingForm(instance=self.existing_booking)
        self.assertIn("term", form.fields)
        self.assertIn("lesson_type", form.fields)
        self.assertIn("student", form.fields)
        self.assertIn("tutor", form.fields)

    def test_form_accepts_valid_data(self):
        """form accepts valid data"""
        form = UpdateBookingForm(instance=self.existing_booking, data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_missing_required_fields(self):
        """form rejects when required fields are missing"""
        required_fields = ["term", "lesson_type", "student", "tutor"]
        for field in required_fields:
            incomplete_data = self.valid_data.copy()
            incomplete_data[field] = ""
            form = UpdateBookingForm(instance=self.existing_booking, data=incomplete_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_form_invalid_nonexistent_student(self):
        """form should be invalid if student does not exist"""
        invalid_data = self.valid_data.copy()
        invalid_data["student"] = 999
        form = UpdateBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('student', form.errors)

    def test_form_invalid_nonexistent_tutor(self):
        """form should be invalid if tutor does not exist"""
        invalid_data = self.valid_data.copy()
        invalid_data["tutor"] = 999
        form = UpdateBookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor', form.errors)

    def test_form_allows_partial_update(self):
        """form allows partial updates that don't violate constraints"""
        partial_update_data = {
            "term": "Term2",
            "lesson_type": "Weekly",
            "student": self.student.id,
            "tutor": self.tutor.id,
        }
        form = UpdateBookingForm(instance=self.existing_booking, data=partial_update_data)
        self.assertTrue(form.is_valid())
        updated_booking = form.save()
        self.assertEqual(updated_booking.term, "Term2")
        self.assertEqual(updated_booking.lesson_type, "Weekly")

    def test_form_rejects_invalid_fields(self):
        """form rejects invalid data for specific fields"""
        invalid_cases = [
            ("term", "InvalidTerm", "term"),
            ("student", 999999, "student"),
            ("tutor", 999999, "tutor"),
        ]
        for field_name, invalid_value, error_field in invalid_cases:
            with self.subTest(field=field_name):
                invalid_data = self.valid_data.copy()
                invalid_data[field_name] = invalid_value
                form = UpdateBookingForm(instance=self.existing_booking, data=invalid_data)
                self.assertFalse(form.is_valid())
                self.assertIn(error_field, form.errors)

    def test_no_of_bookings_does_not_increase_on_update(self):
        """updating a booking does not create a new booking"""
        initial_booking_count = Booking.objects.count()
        form = UpdateBookingForm(instance=self.existing_booking, data=self.valid_data)
        self.assertTrue(form.is_valid())
        form.save()
        final_booking_count = Booking.objects.count()
        self.assertEqual(initial_booking_count, final_booking_count)

    def test_form_invalid_duplicate_booking(self):
        """form should be invalid if a duplicate booking exists"""
        Booking.objects.create(term=self.valid_data["term"], lesson_type="Weekly", student=self.student, tutor=self.tutor)
        form = UpdateBookingForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValidationError):
            form.clean()