from django.test import TestCase
from tutorials.models import User, Student, Tutor
from tutorials.views import populate


class PopulateTestCase(TestCase):
    def setUp(self):
        # Create some sample users
        self.student_user = User.objects.create_user(
            username="@student1", 
            first_name="John", 
            last_name="Doe", 
            email="john.doe@example.com", 
            user_type="student"
        )
        self.tutor_user = User.objects.create_user(
            username="@tutor1", 
            first_name="Jane", 
            last_name="Smith", 
            email="jane.smith@example.com", 
            user_type="tutor"
        )

    def test_populate_creates_students_and_tutors(self):
        # Call the populate function
        populate()

        # Check if Student and Tutor records are created
        self.assertTrue(Student.objects.filter(username=self.student_user).exists())
        self.assertTrue(Tutor.objects.filter(username=self.tutor_user).exists())

        # Verify the data matches
        student = Student.objects.get(username=self.student_user)
        self.assertEqual(student.name, self.student_user.full_name)
        self.assertEqual(student.email, self.student_user.email.lower())

        tutor = Tutor.objects.get(username=self.tutor_user)
        self.assertEqual(tutor.name, self.tutor_user.full_name)
        self.assertEqual(tutor.email, self.tutor_user.email.lower())

    def test_populate_does_not_duplicate_records(self):
        # Call populate twice
        populate()
        populate()

        # Ensure no duplicate Student/Tutor records
        self.assertEqual(Student.objects.filter(username=self.student_user).count(), 1)
        self.assertEqual(Tutor.objects.filter(username=self.tutor_user).count(), 1)
