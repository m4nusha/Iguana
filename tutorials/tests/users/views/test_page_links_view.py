from django.test import TestCase
from django.urls import reverse
from tutorials.tests.helpers import MenuTesterMixin
from django.contrib.auth import get_user_model


class MenuTesterTestCase(TestCase, MenuTesterMixin):
    def setUp(self):
        self.user = self.create_test_user()

    def create_test_user(self):
        User = get_user_model()
        return User.objects.create_user(username="testuser", password="password")

    def test_assert_menu(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse('dashboard'))
        self.assert_menu(response)

    def test_assert_no_menu(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('log_in') + '?next=' + reverse('dashboard'))

    def test_authenticated_user_menu(self):
        self.client.login(username=self.user.username, password="password")
        response = self.client.get(reverse('dashboard'))
        self.assert_menu(response)