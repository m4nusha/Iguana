from django.test import TestCase
from tutorials.forms import SessionForm
from tutorials.models import User, Booking, Session
from datetime import date, time, timedelta


class CreateSessionFormTestCase(TestCase):
    """unit tests for creating a session with the SessionForm"""
    def setUp(self):
        self.student = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        self.tutor = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.booking = Booking.objects.create(term="Term1", student=self.student, tutor=self.tutor)
        self.valid_data = {
            "booking": self.booking.id,
            "session_date": "2025-01-01",
            "session_time": "12:00:00",
            "duration": timedelta(hours=1),
            "lesson_type": "Weekly",
            "venue": "Bush House",
            "amount": 50.00,
            "payment_status": "Pending",
        }
    
    def test_form_accepts_valid_data(self):
        """form accepts valid input"""
        form = SessionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_contains_all_fields(self):
        """form contains all required fields"""
        form = SessionForm()
        expected_fields = ['booking', 'session_date', 'session_time', 'duration', 'lesson_type', 'venue', 'amount', 'payment_status']
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_form_rejects_past_session_date(self):
        """form rejects a session with a date in the past"""
        invalid_data = self.valid_data.copy()
        invalid_data["session_date"] = (date.today() - timedelta(days=1)).isoformat()
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('session_date', form.errors)

    def test_form_rejects_duplicate_session(self):
        """form rejects a duplicate session for the same booking, date, and time"""
        Session.objects.create(
            booking=self.booking,
            session_date="2025-01-01",
            session_time="12:00:00",
            duration=timedelta(hours=1),
            lesson_type="Weekly",
            venue="Bush House",
            amount=50.00,
            payment_status="Pending",
        )
        form = SessionForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertTrue(any(error in form.errors['__all__'] for error in [
            "A session with this booking and date already exists.",
            "This session overlaps with another session for the same booking."
        ]))

    def test_form_rejects_overlapping_sessions(self):
        """form rejects sessions that overlap in time for the same booking"""
        Session.objects.create(
            booking=self.booking,
            session_date="2025-01-01",
            session_time="12:00:00",
            duration=timedelta(hours=2),
            lesson_type="Weekly",
            venue="Bush House",
            amount=50.00,
            payment_status="Pending",
        )
        invalid_data = self.valid_data.copy()
        invalid_data["session_time"] = "13:00:00"
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'], ["This session overlaps with another session for the same booking."])

    def test_form_rejects_invalid_session_date_format(self):
        """form rejects an invalid session date format"""
        invalid_data = self.valid_data.copy()
        invalid_data["session_date"] = "invalid-date"
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('session_date', form.errors)

    def test_form_creates_session_with_valid_data(self):
        """form creates a session when provided valid data"""
        form = SessionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        session = form.save()
        self.assertIsInstance(session, Session)
        self.assertEqual(session.booking, self.booking)
        self.assertEqual(session.session_date, date(2025, 1, 1))
        self.assertEqual(session.session_time, time(12, 0))
        self.assertEqual(session.duration, timedelta(hours=1))
        self.assertEqual(session.lesson_type, "Weekly")
        self.assertEqual(session.venue, "Bush House")
        self.assertEqual(session.amount, 50.00)
        self.assertEqual(session.payment_status, "Pending")

    def test_form_rejects_zero_or_negative_duration(self):
        """form rejects a session with zero or negative duration"""
        invalid_data = self.valid_data.copy()
        invalid_data["duration"] = timedelta(seconds=0)
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("duration", form.errors)

    def test_form_rejects_negative_amount(self):
        """form rejects a session with a negative amount"""
        invalid_data = self.valid_data.copy()
        invalid_data["amount"] = -10.00
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_session_count_increases_after_creation(self):
        """session count increases by 1 after a session is created"""
        initial_count = Session.objects.count()
        form = SessionForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        form.save()
        updated_count = Session.objects.count()
        self.assertEqual(updated_count, initial_count + 1)

    def test_form_validates_choice_fields(self):
        """form rejects invalid choices for lesson_type and venue"""
        invalid_data = self.valid_data.copy()
        invalid_data["lesson_type"] = "InvalidLessonType"
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('lesson_type', form.errors)
        invalid_data["lesson_type"] = "Weekly"
        invalid_data["venue"] = "InvalidVenue"
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('venue', form.errors)

    def test_form_validates_time_format(self):
        """form rejects invalid time format"""
        invalid_data = self.valid_data.copy()
        invalid_data["session_time"] = "25:00:00"
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('session_time', form.errors)
    
    def test_form_validates_payment_status(self):
        """form rejects invalid payment status"""
        invalid_data = self.valid_data.copy()
        invalid_data["payment_status"] = "InvalidStatus"
        form = SessionForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('payment_status', form.errors)