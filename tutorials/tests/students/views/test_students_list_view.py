from django.test import TestCase
from django.urls import reverse
from tutorials.models import Student, User


class StudentsListTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username="@janedoe", email="janedoe@example.com", password="password123", user_type="not specified"
        )
        self.client.login(username="@janedoe", password="password123")

        self.user2 = User.objects.create_user(
            username="@janesmith", email="janesmith@example.com", password="password123", user_type="not specified"
        )
        self.client.login(username="@janesmith", password="password123")


        self.user3 = User.objects.create_user(
            username="@alicejohnson", email="alicejohnson@example.com", password="password123", user_type="not specified"
        )
        self.client.login(username="@alicejohnson", password="password123")


        # Create Student instances manually
        self.student1 = Student.objects.create(
            username=self.user1,
            name="Jane Doe",
            allocated=True,
            payment="Successful",
            email="janedoe@example.com"  # Unique email
        )
        self.student2 = Student.objects.create(
            username=self.user2,
            name="Jane Smith",
            allocated=False,
            payment="Pending",
            email="janesmith@example.com"  # Unique email

        )
        self.student3 = Student.objects.create(
            username=self.user3,
            name="Alice Johnson",
            allocated=True,
            payment="Pending",
            email="alicejohnson@example.com"  # Unique email

        )

        self.url = reverse("students_list")  # URL for the students list view

    def test_students_url(self):
        """Test that the students URL resolves correctly."""
        self.assertEqual(self.url, "/students/")  # Verify the URL is correct

    def test_get_students(self):
        """Test the GET request to display all students."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/students_list.html")
        self.assertIn("students", response.context)
        students = response.context["students"]
        self.assertEqual(students.count(), 3)  # Ensure all students are in the context

    def test_filter_by_allocated_true(self):
        """Test filtering students with allocated=True."""
        response = self.client.get(self.url, {"allocated": "true"})
        students = response.context["students"]
        self.assertEqual(students.count(), 2)  # Only allocated students should appear
        self.assertTrue(all(student.allocated for student in students))

    def test_filter_by_allocated_false(self):
        """Test filtering students with allocated=False."""
        response = self.client.get(self.url, {"allocated": "false"})
        students = response.context["students"]
        self.assertEqual(students.count(), 1)  # Only non-allocated students should appear
        self.assertFalse(any(student.allocated for student in students))

    def test_filter_by_payment_successful(self):
        """Test filtering students with payment='Successful'."""
        response = self.client.get(self.url, {"payment": "Successful"})
        students = response.context["students"]
        self.assertEqual(students.count(), 1)  # Only students with payment "Successful"
        self.assertTrue(all(student.payment == "Successful" for student in students))

    def test_filter_by_payment_pending(self):
        """Test filtering students with payment='Pending'."""
        response = self.client.get(self.url, {"payment": "Pending"})
        students = response.context["students"]
        self.assertEqual(students.count(), 2)  # Only students with payment "Pending"
        self.assertTrue(all(student.payment == "Pending" for student in students))

    def test_search_by_name(self):
        """Test searching for students by name."""
        response = self.client.get(self.url, {"search": "Alice"})
        students = response.context["students"]
        self.assertEqual(students.count(), 1)  # Only the student with "Alice" in their name
        self.assertEqual(students[0].name, "Alice Johnson")

    def test_sort_by_name_ascending(self):
        """Test sorting students by name in ascending order (A-Z)."""
        response = self.client.get(self.url, {"order": "asc"})
        students = response.context["students"]
        self.assertEqual(students[0].name, "Alice Johnson")  # A-Z order
        self.assertEqual(students[1].name, "Jane Doe")
        self.assertEqual(students[2].name, "Jane Smith")

    def test_sort_by_name_descending(self):
        """Test sorting students by name in descending order (Z-A)."""
        response = self.client.get(self.url, {"order": "desc"})
        students = response.context["students"]
        self.assertEqual(students[0].name, "Jane Smith")  # Z-A order
        self.assertEqual(students[1].name, "Jane Doe")
        self.assertEqual(students[2].name, "Alice Johnson")
