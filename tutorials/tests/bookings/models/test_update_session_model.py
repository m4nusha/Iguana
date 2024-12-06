from decimal import Decimal
from django.forms import ValidationError
from django.test import TestCase
from tutorials.models import Session, Booking, User
from datetime import timedelta, date, time

class UpdateSessionModelTest(TestCase):
    """unit tests for updating a Session model"""
    def setUp(self):
        self.student = User.objects.create_user(username="student_user", password="password123", email="student_user@example.com")
        self.tutor = User.objects.create_user(username="tutor_user", password="password123", email="tutor_user@example.com")
        self.booking = Booking.objects.create(term="Term1", student=self.student, tutor=self.tutor)
        self.session = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(14, 30),
            duration=timedelta(hours=1),
            venue=Session.VENUE_BUSH_HOUSE,
            payment_status=Session.PAYMENT_PENDING
        )
        self.session2 = Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 2),
            session_time=time(10, 0),
            duration=timedelta(hours=1),
            venue=Session.VENUE_WATERLOO,
            payment_status=Session.PAYMENT_SUCCESSFUL
        )

    def test_update_session_with_valid_data(self):
        """update session with valid data"""
        self.session.session_date = date(2025, 1, 2)
        self.session.session_time = time(16, 0)
        self.session.save()
        self.session.refresh_from_db()
        self.assertEqual(self.session.session_date, date(2025, 1, 2))
        self.assertEqual(self.session.session_time, time(16, 0))

    def test_update_session_with_invalid_date(self):
        """a session cannot be updated with an invalid date"""
        self.session.session_date = date(2020, 1, 1)
        with self.assertRaises(ValidationError):
            self.session.full_clean()

    def test_update_session_with_overlapping_times(self):
        """a session cannot be updated with overlapping times"""
        Session.objects.create(
            booking=self.booking,
            session_date=date(2025, 1, 1),
            session_time=time(10, 0),
            duration=timedelta(hours=2),
            venue=Session.VENUE_BUSH_HOUSE,
            payment_status=Session.PAYMENT_PENDING
        )
        self.session.session_time = time(11, 0)
        with self.assertRaises(ValidationError):
            self.session.full_clean()

    def test_update_session_with_duplicate_datetime(self):
        """a session cannot be created with a duplicate datetime"""
        Session.objects.create(
            booking=self.booking,
            session_date='2025-01-03',
            session_time='12:30:00',
            duration='01:00:00',
            venue='Bush House',
            payment_status='Pending'
        )
        with self.assertRaises(ValidationError):
            session = Session(
                booking=self.booking,
                session_date='2025-01-03',
                session_time='12:30:00',
                duration='01:00:00',
                venue='Bush House',
                payment_status='Pending'
            )
            session.full_clean()
            session.save()

    def test_update_session_with_invalid_payment_status(self):
        """a session cannot be updated with an invalid payment status"""
        self.session.payment_status = 'INVALID_STATUS'
        with self.assertRaises(ValidationError):
            self.session.save()

    def test_update_session_string_representation(self):
        """the string representation of the session"""
        self.student.username = 'student_user'
        self.tutor.username = 'tutor_user'
        self.student.save()
        self.tutor.save()
        self.session.session_date = '2025-01-03'
        self.session.session_time = '12:30:00'
        self.session.save()
        expected_str = "Session on 2025-01-03 at 12:30:00 for Term1 | Student: student_user | Tutor: tutor_user"
        self.assertEqual(str(self.session), expected_str)

    def test_update_session_with_duplicate_datetime(self):
        """a session cannot be updated with a duplicate date and time"""
        self.session.session_date = self.session2.session_date
        self.session.session_time = self.session2.session_time
        with self.assertRaises(ValidationError):
            self.session.full_clean()
            self.session.save()
