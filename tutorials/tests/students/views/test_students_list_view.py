from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student
from tutorials.models import Student, User  # Import your custom User model
from unittest.mock import patch

class StudentsListTestCase(TestCase):
    @patch('tutorials.views.populate')  # Mock populate in the relevant module
    def setUp(self, mock_populate):
        mock_populate.return_value = None  # Disable the actual populate logic
        # Test setup logic
        # Create User instances with user_type='student' (this will automatically create Student instances)
        self.user1 = User.objects.create_user(
            username="@johndoe", email="johndoe@example.com", password="password123", user_type="student"
        )
        self.user2 = User.objects.create_user(
            username="@janesmith", email="janesmith@example.com", password="password123", user_type="student"
        )
        self.user3 = User.objects.create_user(
            username="@alicejohnson", email="alicejohnson@example.com", password="password123", user_type="student"
        )

        # Fetch the automatically created Student instances
        self.student1 = Student.objects.get(username=self.user1)
        self.student2 = Student.objects.get(username=self.user2)
        self.student3 = Student.objects.get(username=self.user3)

        # Update additional fields for Student instances
        self.student1.name = "John Doe"
        self.student1.allocated = True
        self.student1.payment = "Successful"
        self.student1.save()

        self.student2.name = "Jane Smith"
        self.student2.allocated = False
        self.student2.payment = "Pending"
        self.student2.save()

        self.student3.name = "Alice Johnson"
        self.student3.allocated = True
        self.student3.payment = "Pending"
        self.student3.save()

        self.url = reverse("students")  # URL for the students list view

    def test_students_url(self):
        self.assertEqual(self.url, "/students/")  # Verify the URL is correct

    def test_get_students(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students_list.html")
        self.assertIn("students", response.context)
        students = response.context["students"]
        self.assertEqual(students.count(), 3)  # Ensure all students are in the context

    def test_filter_by_allocated_true(self):
        response = self.client.get(self.url, {"allocated": "true"})
        students = response.context["students"]
        self.assertEqual(students.count(), 2)  # Only allocated students should appear
        self.assertTrue(all(student.allocated for student in students))

    def test_filter_by_allocated_false(self):
        response = self.client.get(self.url, {"allocated": "false"})
        students = response.context["students"]
        self.assertEqual(students.count(), 1)  # Only non-allocated students should appear
        self.assertFalse(any(student.allocated for student in students))

    def test_filter_by_payment_successful(self):
        response = self.client.get(self.url, {"payment": "Successful"})
        students = response.context["students"]
        self.assertEqual(students.count(), 1)  # Only students with payment "Successful"
        self.assertTrue(all(student.payment == "Successful" for student in students))

    def test_filter_by_payment_pending(self):
        response = self.client.get(self.url, {"payment": "Pending"})
        students = response.context["students"]
        self.assertEqual(students.count(), 2)  # Only students with payment "Pending"
        self.assertTrue(all(student.payment == "Pending" for student in students))

    def test_search_by_name(self):
        response = self.client.get(self.url, {"search": "Jane"})
        students = response.context["students"]
        self.assertEqual(students.count(), 1)  # Only the student with "Jane" in their name
        self.assertEqual(students[0].name, "Jane Smith")

    def test_sort_by_name_ascending(self):
        response = self.client.get(self.url, {"order": "asc"})
        students = response.context["students"]
        self.assertEqual(students[0].name, "Alice Johnson")  # A-Z order
        self.assertEqual(students[1].name, "Jane Smith")
        self.assertEqual(students[2].name, "John Doe")

    def test_sort_by_name_descending(self):
        response = self.client.get(self.url, {"order": "desc"})
        students = response.context["students"]
        self.assertEqual(students[0].name, "John Doe")  # Z-A order
        self.assertEqual(students[1].name, "Jane Smith")
        self.assertEqual(students[2].name, "Alice Johnson")
