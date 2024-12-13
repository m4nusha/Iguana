from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User


class EditUserViewTest(TestCase):
    """Test for the 'edit_user' view."""
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(username='admin', email='admin@example.com', password='admin123')
        self.normal_user = get_user_model().objects.create_user(username='user', email='user@example.com', password='user123')
        self.user_to_edit = User.objects.create_user(username='user1', email='user1@example.com', first_name='Jane', last_name='Doe', user_type='student')
        self.url = reverse('edit_users_type', kwargs={'user_id': self.user_to_edit.id})

    def test_login_required_redirect(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}', status_code=302, target_status_code=200)

    def test_authenticated_user_can_access_edit_form(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Jane"')

    def test_post_invalid_data_does_not_update_user(self):
        self.client.login(username='admin', password='admin123')
        invalid_data = {
            'username': '',
            'email': 'invalid_email',
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_users_type.html')
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Enter a valid email address.')
        self.user_to_edit.refresh_from_db()
        self.assertEqual(self.user_to_edit.username, 'user1')

    def test_anonymous_user_redirect_to_login_on_post(self):
        valid_data = {
            'username': 'new_user1',
            'email': 'new_user1@example.com',
            'first_name': 'Janet',
            'last_name': 'Smith',
            'user_type': 'teacher',
        }
        response = self.client.post(self.url, data=valid_data)
        self.assertRedirects(response, f'/log_in/?next={self.url}')
        self.user_to_edit.refresh_from_db()
        self.assertEqual(self.user_to_edit.username, 'user1')