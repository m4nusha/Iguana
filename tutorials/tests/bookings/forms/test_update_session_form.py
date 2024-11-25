
# additional tests to add: duplicate session with same booking, time, date

from django.test import TestCase
from tutorials.forms import UpdateSessionForm
from tutorials.models import Session, Booking, User
from datetime import date, time, timedelta

class UpdateSessionFormTestCase(TestCase):
    """unit tests for the Update Session Form"""
    def setUp(self):
        self.student = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        self.tutor = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.existing_booking = Booking.objects.create(term="Term1", student=self.student, tutor=self.tutor)
        self.existing_session = Session.objects.create(
            booking=self.existing_booking,
            session_date=date(2024, 11, 25),
            session_time=time(10, 0),
            duration=timedelta(hours=1),
            lesson_type=Session.TYPE_WEEKLY,
            venue=Session.VENUE_BUSH_HOUSE,
            amount=50.00,
            payment_status=Session.PAYMENT_PENDING
        )
        self.valid_data = {
            "session_date": date(2024, 11, 26),
            "session_time": time(11, 0),
            "duration": timedelta(hours=1),
            "lesson_type": Session.TYPE_FORTNIGHT,
            "venue": Session.VENUE_WATERLOO,
            "amount": 60.00,
            "payment_status": Session.PAYMENT_SUCCESSFUL,
            "booking": self.existing_booking.id
        }

    def test_form_contains_required_fields(self):
        """form contains required fields"""
        form = UpdateSessionForm(instance=self.existing_session)
        self.assertIn("session_date", form.fields)
        self.assertIn("session_time", form.fields)
        self.assertIn("duration", form.fields)
        self.assertIn("lesson_type", form.fields)
        self.assertIn("venue", form.fields)
        self.assertIn("amount", form.fields)
        self.assertIn("payment_status", form.fields)

    def test_form_accepts_valid_data(self):
        """form accepts valid data"""
        form = UpdateSessionForm(instance=self.existing_session, data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_rejects_missing_required_fields(self):
        """form rejects when required fields are missing"""
        required_fields = ["session_date", "session_time", "duration", "lesson_type", "venue", "amount", "payment_status"]
        for field in required_fields:
            incomplete_data = self.valid_data.copy()
            incomplete_data[field] = ""
            form = UpdateSessionForm(instance=self.existing_session, data=incomplete_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_form_rejects_invalid_session_date(self):
        """form rejects invalid session date"""
        invalid_data = self.valid_data.copy()
        invalid_data["session_date"] = date(2020, 11, 25) 
        form = UpdateSessionForm(instance=self.existing_session, data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("session_date", form.errors)
        self.assertEqual(form.errors["session_date"], ["Session date cannot be in the past."])

    def test_form_rejects_invalid_session_time(self):
        """form rejects invalid session time format"""
        invalid_data = {
            "session_time": "25:00",
        }
        session = Session.objects.create(
            booking=self.existing_booking, 
            session_date="2025-01-01",  
            session_time="10:00", 
            duration=timedelta(hours=1), 
            lesson_type="Weekly", 
            venue="Bush House", 
            amount=100.00, 
            payment_status="Pending"
        )
        form = UpdateSessionForm(instance=session, data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("session_time", form.errors)
        self.assertEqual(form.errors["session_time"], ["Enter a valid time."])

    def test_form_rejects_invalid_amount(self):
        """form rejects invalid amount"""
        invalid_data = {
            "amount": "-100.00",
        }
        session = Session.objects.create(
            booking=self.existing_booking, 
            session_date="2025-01-01",  
            session_time="10:00", 
            duration=timedelta(hours=1), 
            lesson_type="Weekly", 
            venue="Bush House", 
            amount=100.00, 
            payment_status="Pending"
        )
        form = UpdateSessionForm(instance=session, data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)
        self.assertEqual(form.errors["amount"], ["Ensure this value is greater than or equal to 0."])

    def test_form_keeps_existing_session_on_no_changes(self):
        """submitting form with no changes keeps the existing session"""
        form = UpdateSessionForm(instance=self.existing_session, data={
            "session_date": self.existing_session.session_date,
            "session_time": self.existing_session.session_time,
            "duration": self.existing_session.duration,
            "lesson_type": self.existing_session.lesson_type,
            "venue": self.existing_session.venue,
            "amount": self.existing_session.amount,
            "payment_status": self.existing_session.payment_status,
        })
        self.assertTrue(form.is_valid())
        unchanged_session = form.save()
        self.assertEqual(unchanged_session, self.existing_session)

    def test_form_rejects_invalid_fields(self):
        """form rejects invalid data for specific fields"""
        invalid_cases = [
            ("session_date", "InvalidDate", "session_date"),
            ("session_time", "InvalidTime", "session_time"),
            ("amount", -10.00, "amount"),
        ]
        for field_name, invalid_value, error_field in invalid_cases:
            with self.subTest(field=field_name):
                invalid_data = self.valid_data.copy()
                invalid_data[field_name] = invalid_value
                form = UpdateSessionForm(instance=self.existing_session, data=invalid_data)
                self.assertFalse(form.is_valid())
                self.assertIn(error_field, form.errors)

    def test_no_of_sessions_does_not_increase_on_update(self):
        """updating a session does not create a new session"""
        initial_session_count = Session.objects.count()
        form = UpdateSessionForm(instance=self.existing_session, data=self.valid_data)
        self.assertTrue(form.is_valid())
        form.save()
        final_session_count = Session.objects.count()
        self.assertEqual(initial_session_count, final_session_count)