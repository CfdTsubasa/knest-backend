from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

User = get_user_model()

@override_settings(
    FRONTEND_URL='http://localhost:3000',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'display_name': 'Test User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration(self):
        url = reverse('users:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'display_name': 'New User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        url = reverse('users:token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_profile(self):
        url = reverse('users:profile')
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_password_change(self):
        url = reverse('users:password_change')
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newtestpass123',
            'new_password2': 'newtestpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newtestpass123'))

    def test_password_reset_request(self):
        url = reverse('users:password_reset')
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.password_reset_token)

    def test_password_reset_confirm(self):
        # パスワードリセットトークンを設定
        self.user.password_reset_token = 'test-token'
        self.user.password_reset_token_created = timezone.now()
        self.user.save()

        url = reverse('users:password_reset_confirm')
        data = {
            'token': 'test-token',
            'new_password': 'resetpass123',
            'new_password2': 'resetpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.password_reset_token)
        self.assertTrue(self.user.check_password('resetpass123')) 