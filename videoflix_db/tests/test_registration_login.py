# from django.urls import reverse
# from django.conf import settings
# from django.utils import timezone
# from rest_framework.test import APIClient, APITestCase
# from rest_framework import status
# from videoflix_db.models import UserProfil
# from .test_data import create_user, create_incative_user
# from unittest.mock import patch
# from datetime import timedelta
# from django.contrib.auth import get_user_model


# User = get_user_model()


# class CreateUserTests(APITestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.url = reverse('registration-detail')

#     def test_create_user(self):
#         data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword',
#             'repeated_password': 'examplePassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_duplicate_user(self):
#         data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword',
#             'repeated_password': 'examplePassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(User.objects.count(), 1)
#         response_duplicate = self.client.post(self.url, data, format='json')
#         self.assertEqual(response_duplicate.status_code,
#                          status.HTTP_201_CREATED)
#         self.assertEqual(User.objects.count(), 1)

#     def test_fail_password_create_user(self):
#         data = {
#             'email': 'example@mail.de',
#             'password': 'rightPassword',
#             'repeated_password': 'wrongPassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], "Passwords don't match")

#     def test_fail_email_create_user(self):
#         data = {
#             'email': 'noEmail',
#             'password': 'rightPassword',
#             'repeated_password': 'rightPassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_fail_email_no_data_create_user(self):
#         data = {'repeated_password': 'rightPassword'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], "Email and password required")

#     def test_invalid_method_create_user(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code,
#                          status.HTTP_405_METHOD_NOT_ALLOWED)
#         data = {'email': 'exampleUsername'}
#         response = self.client.patch(self.url, data, format='json')
#         self.assertEqual(response.status_code,
#                          status.HTTP_405_METHOD_NOT_ALLOWED)
#         response = self.client.delete(self.url)
#         self.assertEqual(response.status_code,
#                          status.HTTP_405_METHOD_NOT_ALLOWED)


# class UserLoginTests(APITestCase):

#     def setUp(self):
#         self.user = create_user()
#         self.inactive_user = create_incative_user()
#         self.client = APIClient()
#         self.url = reverse('login-detail')

#     def test_login_user(self):
#         data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('access_token', response.cookies)
#         self.assertIn('refresh_token', response.cookies)

#     def test_fail_email_login_user(self):
#         data = {
#             'email': 'wrong@mail.com',
#             'password': 'examplePassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('Incorrect email or password', str(response.data['error']))

#     def test_fail_password_login_user(self):
#         data = {
#             'email': 'example@mail.de',
#             'password': 'wrongPassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('Incorrect email or password', str(response.data['error']))

#     def test_fail_login_user_unauthorized(self):
#         data = {
#             'email': 'inactiveuser@mail.de',
#             'password': 'examplePassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)