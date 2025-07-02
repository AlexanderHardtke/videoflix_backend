from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from videoflix_db.models import EmailConfirmationToken, UserProfil
from .test_data import create_user, create_incative_user
from unittest.mock import patch
from datetime import timedelta


class CreateUserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('registration-detail')
        settings.EMAIL_CONFIRM_URL = 'https://mocked-url.com'
        patcher = patch('videoflix_db.api.views.requests.post')
        self.mock_post = patcher.start()
        self.addCleanup(patcher.stop)

    def test_create_user(self):
        data = {
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.mock_post.assert_called_once()
        self.assertEqual(response.data['error'], 'Confirm your email address')

    def test_duplicate_user(self):
        data = {
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        response_duplicate = self.client.post(self.url, data, format='json')
        self.assertEqual(response_duplicate.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_duplicate.data['error'], 'Confirm your email address')
        self.assertEqual(self.mock_post.call_count, 2)

    def test_fail_password_create_user(self):
        data = {
            'email': 'example@mail.de',
            'password': 'rightPassword',
            'repeated_password': 'wrongPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_email_create_user(self):
        data = {
            'email': 'noEmail',
            'password': 'rightPassword',
            'repeated_password': 'rightPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method_create_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = {'email': 'exampleUsername'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserLoginTests(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.inactive_user = create_incative_user()
        self.client = APIClient()
        self.url = reverse('login-detail')

    def test_login_user(self):
        data = {
            'email': 'example@mail.de',
            'password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.data['email'], data['email'])
        self.assertIsInstance(response.data['token'], str)
        self.assertIsInstance(response.data['user_id'], int)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_email_login_user(self):
        data = {
            'email': 'wrong@mail.com',
            'password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Incorrect username or password')

    def test_fail_password_login_user(self):
        data = {
            'username': 'example@mail.de',
            'password': 'wrongPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Incorrect username or password')

    def test_fail_login_user_authorized(self):
        data = {
            'username': 'inactiveuser@mail.de',
            'password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Confirm your email address')


class ActivateAccountTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('registration-detail')
        settings.EMAIL_CONFIRM_URL = 'https://mocked-url.com'
        patcher = patch('videoflix_db.api.views.requests.post')
        self.mock_post = patcher.start()
        self.addCleanup(patcher.stop)
        data = {
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword'
        }
        self.client.post(self.url, data, format='json')
        self.token = EmailConfirmationToken.objects.get(user__email='example@mail.de').token

    def test_activate_account(self):
        url = reverse('confirm-detail')
        response = self.client.post(url, {'token': self.token}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], 'Email confirmed')
        user = UserProfil.objects.get(email='example@mail.de')
        self.assertTrue(user.email_confirmed)

    def test_invalid_token_activate_account(self):
        url = reverse('confirm-detail')
        response = self.client.post(url, {'token': 'invalid'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Token is not valid or expired')
        user = UserProfil.objects.get(email='example@mail.de')
        self.assertFalse(user.email_confirmed)

    def test_no_token_activate_account(self):
        url = reverse('confirm-detail')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Token is not valid or expired')
        user = UserProfil.objects.get(email='example@mail.de')
        self.assertFalse(user.email_confirmed)

    def test_expired_token_activate_account(self):
        user = UserProfil.objects.get(email='example@mail.de')
        expired_time = timezone.now() - timedelta(days=2)
        token = EmailConfirmationToken.objects.create(
            user=user,
            token='expired-token-123'
        )
        token.created_at = expired_time
        token.save()
        url = reverse('confirm-detail')
        response = self.client.post(url, {'token': token.token}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Token is not valid or expired')
        self.assertFalse(user.email_confirmed)

    def test_invalid_method_activate_account(self):
        url = reverse('confirm-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(url, {'token': self.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
