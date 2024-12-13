from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User


class UsersListViewTest(TestCase):
    """Tests for the 'users_list' view."""
    fixtures = ['tutorials/tests/users/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('users_list')
        
        self.admin_user = get_user_model().objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='admin123', 
        )
        self.normal_user = get_user_model().objects.create_user(
            username='user', 
            email='user@example.com', 
            password='user123', 
        )
        self.user1 = User.objects.create_user(
            username='user1', 
            email='user1@example.com', 
            first_name='Jane', 
            last_name='Doe', 
            user_type='tutor'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            email='user2@example.com', 
            first_name='Jane', 
            last_name='Smith', 
            user_type='student'
        )

    def test_login_required_redirect(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}', status_code=302, target_status_code=200)

    def test_authenticated_user_can_access_list(self):
        self.client.login(username='user', password='user123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_access_list(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_filter_users_by_user_type(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url, {'user_type': 'tutor'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(user.user_type == 'tutor' for user in response.context['users']))
        response = self.client.get(self.url, {'user_type': 'student'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(user.user_type == 'student' for user in response.context['users']))

    def test_search_users_by_name(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url, {'search': 'Jane'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all('Jane' in (user.first_name or '') for user in response.context['users']))
        response = self.client.get(self.url, {'search': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 0)

    def test_search_users_by_name(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url, {'search': 'Jane'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all('Jane' in (user.first_name or '') for user in response.context['users']))
        response = self.client.get(self.url, {'search': 'Blob'})
        self.assertEqual(response.status_code, 200)
        users = response.context['users']
        self.assertEqual(len(users), 0)

    def test_combined_filter_search_and_order(self):
        self.client.login(username='admin', password='admin123')
        params = {'user_type': 'tutor', 'search': 'Jane', 'order_by': 'asc'}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        users = response.context['users']
        self.assertGreater(len(users), 0, "No users found with the combined filter/search criteria")
        self.assertTrue(all(user.user_type == 'tutor' for user in users))
        self.assertTrue(all('Jane' in (user.first_name or '') for user in users))
        if len(users) > 1:
            self.assertLessEqual(users[0].first_name, users[1].first_name)