from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .test_data import create_user, create_incative_user


class CreateUserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('registration-detail')

    def test_create_user(self):
        data = {
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["registration"], "Confirm your email address")

    def test_duplicate_user(self):
        data = {
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        response_duplicate = self.client.post(self.url, data, format='json')
        self.assertEqual(response_duplicate.status_code,
                         status.HTTP_201_CREATED)
        self.assertEqual(
            response_duplicate.data["registration"], "Confirm your email address")

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
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        data = {'email': 'exampleUsername'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        response = self.client.delete(self.url)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )


class UserLoginTests(APITestCase):

    def setUp(self):
        self.user = create_user()
        self.inactive_user = create_incative_user()
        self.client = APIClient()
        self.url = reverse('login-detail')

    def test_login_user(self):
        data = {
            'username': 'example@mail.de',
            'password': 'examplePassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.data['username'], data['username'])
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
        self.assertEqual(response.data['registration'], 'Confirm your email address')
