# from django.urls import reverse
# from django.conf import settings
# from django.utils import timezone
# from rest_framework.test import APIClient, APITestCase
# from rest_framework import status
# from videoflix_db.models import UserProfil, PasswordForgetToken
# from .test_data import create_user
# from unittest.mock import patch
# from datetime import timedelta


# class PasswordSendResetTests(APITestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user()
#         self.url = reverse('reset-detail')
#         settings.EMAIL_CONFIRM_URL = 'https://mocked-url.com'
#         patcher = patch('videoflix_db.api.views.requests.post')
#         self.mock_post = patcher.start()
#         self.addCleanup(patcher.stop)

#     def test_create_reset_password(self):
#         data = {'email': 'example@mail.de'}
#         response = self.client.post(self.url, data, format='json')
#         self.token = PasswordForgetToken.objects.get(
#             user__email='example@mail.de').token
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(self.token, 'Token generated')

#     def test_wrong_email_create_reset_password(self):
#         data = {'email': 'wrong@mail.de'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         token_exists = PasswordForgetToken.objects.filter(
#             user__email='wrong@mail.de'
#         ).exists()
#         self.assertFalse(token_exists, 'No token for wrong email')

#     def test_no_email_create_reset_password(self):
#         data = {'no-email': 'no-email'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_invalid_method_create_reset_password(self):
#         response = self.client.get(self.url)
#         self.assertEqual(
#             response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
#         )
#         data = {'email': 'example@mail.de'}
#         response = self.client.patch(self.url, data, format='json')
#         self.assertEqual(
#             response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
#         )
#         response = self.client.delete(self.url)
#         self.assertEqual(
#             response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
#         )


# class PasswordChangeTests(APITestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user()
#         url = reverse('reset-detail')
#         settings.EMAIL_CONFIRM_URL = 'https://mocked-url.com'
#         patcher = patch('videoflix_db.api.views.requests.post')
#         self.mock_post = patcher.start()
#         self.addCleanup(patcher.stop)
#         data = {'email': 'example@mail.de'}
#         self.client.post(url, data, format='json')
#         self.token = PasswordForgetToken.objects.get(user__email='example@mail.de').token
#         self.url = reverse('change-detail')

#     def test_change_password(self):
#         data = {
#             'password': 'newPassword',
#             'repeated_password': 'newPassword',
#             'token': self.token
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['success'], 'Password changed successfully')
#         user = UserProfil.objects.get(email='example@mail.de')
#         self.assertTrue(user.check_password('newPassword'))

#     def test_invalid_token_change_password(self):
#         data = {
#             'password': 'newPassword',
#             'repeated_password': 'newPassword',
#             'token': 'invalidToken'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')

#     def test_no_token_change_password(self):
#         data = {
#             'password': 'newPassword',
#             'repeated_password': 'newPassword'
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')

#     def test_no_password_change_password(self):
#         data = {
#             'password': '',
#             'repeated_password': '',
#             'token': self.token
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Password is missing')

#     def test_expired_token_change_password(self):
#         expired_time = timezone.now() - timedelta(days=2)
#         token = PasswordForgetToken.objects.create(
#             user=self.user,
#             token='expired-token-123'
#         )
#         token.created_at = expired_time
#         token.save()
#         data = {
#             'password': 'newPassword',
#             'repeated_password': 'newPassword',
#             'token': token.token
#         }
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')
#         self.assertFalse(self.user.check_password('newPassword'))

#     def test_invalid_method_change_password(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
#         data = {
#             'password': 'newPassword',
#             'repeated_password': 'newPassword',
#             'token': self.token
#         }
#         response = self.client.patch(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
#         response = self.client.delete(self.url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
