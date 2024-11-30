from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import User

class UserListViewTestCase(TestCase):
    """Tests for the list_users view."""

    def setUp(self):
        self.client = Client()
        self.student1 = User.objects.create_user(username='student1', first_name='Alice', last_name='Brown', user_type='student', email='alice@example.com')
        self.student2 = User.objects.create_user(username='student2', first_name='Charlie', last_name='Davis', user_type='student', email='charlie@example.com')
        self.tutor1 = User.objects.create_user(username='tutor1', first_name='Bob', last_name='Smith', user_type='tutor', email='bob@example.com')

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('list_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/list_users.html')

    def test_view_displays_all_users(self):
        response = self.client.get(reverse('list_users'))
        self.assertContains(response, 'Alice')
        self.assertContains(response, 'Charlie')
        self.assertContains(response, 'Bob')

    def test_filter_by_user_type(self):
        response = self.client.get(reverse('list_users') + '?user_type=student')
        self.assertContains(response, 'Alice')
        self.assertContains(response, 'Charlie')
        self.assertNotContains(response, 'Bob')

        response = self.client.get(reverse('list_users') + '?user_type=tutor')
        self.assertContains(response, 'Bob')
        self.assertNotContains(response, 'Alice')
        self.assertNotContains(response, 'Charlie')

    def test_search_users_by_name(self):
        response = self.client.get(reverse('list_users') + '?search=Alice')
        self.assertContains(response, 'Alice')
        self.assertNotContains(response, 'Bob')
        self.assertNotContains(response, 'Charlie')

    def test_order_users_alphabetically(self):
        response = self.client.get(reverse('list_users') + '?order_by=asc')
        content = response.content.decode()
        self.assertTrue(content.index('Alice') < content.index('Bob') < content.index('Charlie'))

        response = self.client.get(reverse('list_users') + '?order_by=desc')
        content = response.content.decode()
        self.assertTrue(content.index('Charlie') < content.index('Bob') < content.index('Alice'))

    def test_combined_filters_and_search(self):
        response = self.client.get(reverse('list_users') + '?user_type=student&search=Alice')
        self.assertContains(response, 'Alice')
        self.assertNotContains(response, 'Charlie')
        self.assertNotContains(response, 'Bob')
