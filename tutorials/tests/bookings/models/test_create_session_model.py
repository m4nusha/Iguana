
# additional tests: session with amount zero

from decimal import Decimal
from django.forms import ValidationError
from django.test import TestCase
from tutorials.models import Booking, User, Session
from datetime import timedelta, date, time

class CreateSessionModelTest(TestCase):
    """unit tests for the Session model"""
    def setUp(self):
        self.student = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        self.tutor = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.booking = Booking.objects.create(term="Term1", student=self.student, tutor=self.tutor)

    def test_create_session_with_valid_data(self):
        """create a session with valid data"""
        session = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(14, 30),
            duration=timedelta(hours=1),
            lesson_type=Session.TYPE_WEEKLY,
            venue=Session.VENUE_BUSH_HOUSE,
            amount=Decimal('100.00'),
            payment_status=Session.PAYMENT_PENDING
        )
        self.assertEqual(session.session_date, date(2025, 1, 1))
        self.assertEqual(session.session_time, time(14, 30))
        self.assertEqual(session.amount, Decimal('100.00'))
        self.assertEqual(session.payment_status, Session.PAYMENT_PENDING)

    def test_session_with_negative_amount(self):
        """a session with a negative amount should raise a validation error"""
        with self.assertRaises(ValidationError):
            session = Session(booking=self.booking, session_date=date(2025, 1, 1), session_time=time(14, 30), duration=timedelta(hours=1), amount=Decimal('-50.00'))
            session.full_clean()

    def test_session_with_invalid_payment_status(self):
        """a session with an invalid payment status should raise a validation error"""
        with self.assertRaises(ValidationError):
            session = Session(booking=self.booking, session_date=date(2025, 1, 1), session_time=time(14, 30), duration=timedelta(hours=1), amount=Decimal('100.00'), payment_status="INVALID_STATUS")
            session.full_clean()

    def test_session_with_overlapping_times(self):
        """sessions with overlapping times for the same booking should raise a validation error"""
        Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(10, 0),
            duration=timedelta(hours=2),
            lesson_type=Session.TYPE_WEEKLY,
            venue=Session.VENUE_BUSH_HOUSE,
            amount=Decimal('100.00'),
            payment_status=Session.PAYMENT_PENDING
        )
        with self.assertRaises(ValidationError):
            session = Session(booking=self.booking, session_date=date(2025, 1, 1), session_time=time(11, 0), duration=timedelta(hours=1), lesson_type=Session.TYPE_BIWEEKLY, venue=Session.VENUE_WATERLOO, amount=Decimal('150.00'), payment_status=Session.PAYMENT_PENDING)
            session.full_clean()

    def test_session_with_past_date(self):
        """a session cannot be created with a past date"""
        with self.assertRaises(ValidationError):
            session = Session(booking=self.booking, session_date=date(2020, 1, 1), session_time=time(10, 0), duration=timedelta(hours=1), amount=Decimal('100.00'), payment_status=Session.PAYMENT_PENDING)
            session.full_clean()

    def test_multiple_sessions_for_same_booking(self):
        """multiple sessions can be created for the same booking, as long as dates don't overlap"""
        Session.objects.create(booking=self.booking, session_date=date(2025, 1, 1), session_time=time(10, 0), duration=timedelta(hours=1), lesson_type=Session.TYPE_WEEKLY, venue=Session.VENUE_BUSH_HOUSE, amount=Decimal('100.00'), payment_status=Session.PAYMENT_PENDING)
        Session.objects.create(booking=self.booking, session_date=date(2025, 1, 2), session_time=time(10, 0), duration=timedelta(hours=1), lesson_type=Session.TYPE_BIWEEKLY, venue=Session.VENUE_WATERLOO, amount=Decimal('150.00'), payment_status=Session.PAYMENT_SUCCESSFUL)
        self.assertEqual(Session.objects.count(), 2)

    def test_create_session_with_duplicate_datetime(self):
        """a session with a duplicate date and time should raise a validation error"""
        Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 3),
            session_time=time(12, 30),
            duration=timedelta(hours=1),
            lesson_type=Session.TYPE_WEEKLY,
            venue=Session.VENUE_BUSH_HOUSE,
            amount=Decimal('100.00'),
            payment_status=Session.PAYMENT_PENDING
        )
        with self.assertRaises(ValidationError):
            session = Session(booking=self.booking, session_date=date(2025, 1, 3), session_time=time(12, 30), duration=timedelta(hours=1), lesson_type=Session.TYPE_WEEKLY, venue=Session.VENUE_BUSH_HOUSE, amount=Decimal('100.00'), payment_status=Session.PAYMENT_PENDING)
            session.full_clean()

    def test_create_session_with_invalid_duration(self):
        """a session with a duration under 1 should raise a validation error"""
        with self.assertRaises(ValidationError):
            session = Session(booking=self.booking, session_date=date(2025, 1, 1), session_time=time(10, 0), duration=timedelta(hours=0), amount=Decimal('100.00'), payment_status=Session.PAYMENT_PENDING)
            session.full_clean()

    def test_create_session_string_representation(self):
        """the string representation of a session"""
        session = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 3),
            session_time=time(12, 30),
            duration=timedelta(hours=2),
            lesson_type=Session.TYPE_WEEKLY,
            venue=Session.VENUE_BUSH_HOUSE,
            amount=Decimal('100.00'),
            payment_status=Session.PAYMENT_PENDING
        )
        expected_str = "Session on 2025-01-03 at 12:30:00 for Term1 | Student: student_user | Tutor: tutor_user"
        self.assertEqual(str(session), expected_str)
