from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CreateUserViewTest(TestCase):
    """Test for the 'create_user' view."""
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(username='admin', email='admin@example.com', password='admin123')
        self.normal_user = get_user_model().objects.create_user(username='user', email='user@example.com', password='user123')
        self.url = reverse('create_user')
        
    def test_login_required_redirect(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}', status_code=302, target_status_code=200)

    def test_authenticated_user_can_access_create_user_form(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="')
    
    def test_create_user_with_invalid_data(self):
        self.client.login(username='admin', password='admin123')
        invalid_data = {
            'username': '',
            'email': 'invalid_email',
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_user.html')
        self.assertContains(response, 'This field is required.')
        self.assertContains(response, 'Enter a valid email address.')
        
    def test_anonymous_user_redirects_to_login_on_post(self):
        valid_data = {
            'username': 'newuser1',
            'email': 'newuser1@example.com',
            'password': 'password123',
        }
        response = self.client.post(self.url, data=valid_data)
        self.assertRedirects(response, f'/log_in/?next={self.url}')

    def test_create_user_get_when_logged_in(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_user.html')