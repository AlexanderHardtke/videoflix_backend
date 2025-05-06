from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class CreateUserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('registration-detail')

    def test_create_user(self):
        data = {
            'username': 'exampleUsername',
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword',
            'type': 'customer'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        partial_response = {
            'username': 'exampleUsername',
            'email': 'example@mail.de',
        }
        for key, value in partial_response.items():
            self.assertEqual(response.data[key], value)

        self.assertIsInstance(response.data['token'], str)
        self.assertIsInstance(response.data['user_id'], int)

    def test_duplicate_user(self):
        data = {
            'username': 'exampleUsername',
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword',
            'type': 'customer'
        }
        response = self.client.post(self.url, data, format='json')
        response_duplicate = self.client.post(self.url, data, format='json')
        self.assertWarnsMessage(response_duplicate.data,
                                'A user with that username already exists.')
        self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_create_user(self):
        data = {
            'username': 'exampleUsername',
            'email': 'example@mail.de',
            'password': 'rightPassword',
            'repeated_password': 'wrongPassword',
            'type': 'customer'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method_create_user(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        data = {'username': 'exampleUsername'}
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
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.url = reverse('login')

    def test_login_user(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.data['username'], data['username'])
        self.assertIsInstance(response.data['token'], str)
        self.assertIsInstance(response.data['user_id'], int)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_login_user(self):
        data = {
            'username': 'wrongUsername',
            'password': 'wrongPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
