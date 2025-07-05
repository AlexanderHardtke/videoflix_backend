# from django.urls import reverse
# from django.conf import settings
# from django.utils import timezone
# from rest_framework.test import APIClient, APITestCase
# from rest_framework import status
# from videoflix_db.models import UserProfil
# from .test_data import create_user
# from unittest.mock import patch
# from datetime import timedelta
# from authemail.models import PasswordResetCode


# class PasswordSendResetTests(APITestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user()
#         self.url = reverse('reset-detail')

#     def test_create_reset_password(self):
#         data = {'email': 'example@mail.de'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.token = PasswordResetCode.objects.filter(user__email='example@mail.de').first()
#         self.assertIsNotNone(self.token)

#     def test_wrong_email_create_reset_password(self):
#         data = {'email': 'wrong@mail.de'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         token_exists = PasswordResetCode.objects.filter(
#             user__email='wrong@mail.de'
#         ).exists()
#         self.assertFalse(token_exists, 'No token for wrong email')

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
#         data = {'email': 'example@mail.de'}
#         self.client.post(url, data, format='json')
#         self.token = PasswordResetCode.objects.filter(user__email='example@mail.de').first()
#         self.url = reverse('verify-detail')
#         self.change_url = reverse('change-detail')
        

#     def test_change_password(self):
#         verify_response = self.client.get(self.url + f'?code={self.token.code}')
#         self.assertEqual(verify_response.status_code, 200)
#         data = {
#             'password': 'newPassword',
#             'repeatPw': 'newPassword',
#             'code': self.token.code
#         }
#         response = self.client.post(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['success'], 'Password changed successfully')
#         user = UserProfil.objects.get(email='example@mail.de')
#         self.assertTrue(user.check_password('newPassword'))

#     def test_invalid_token_change_password(self):
#         verify_response = self.client.get(self.url + f'?code={self.token.code}')
#         self.assertEqual(verify_response.status_code, 200)
#         data = {
#             'password': 'newPassword',
#             'repeatPw': 'newPassword',
#             'code': 'invalidToken'
#         }
#         response = self.client.post(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')

#     def test_no_token_change_password(self):
#         verify_response = self.client.get(self.url + f'?code={''}')
#         self.assertEqual(verify_response.status_code, 400)
#         data = {
#             'password': 'newPassword',
#             'repeated_password': 'newPassword'
#         }
#         response = self.client.post(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')

#     def test_no_password_change_password(self):
#         verify_response = self.client.get(self.url + f'?code={self.token.code}')
#         self.assertEqual(verify_response.status_code, 200)
#         data = {
#             'password': '',
#             'repeated_password': '',
#             'code': self.token.code
#         }
#         response = self.client.post(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Password is missing')

#     def test_expired_token_change_password(self):
#         token = PasswordResetCode.objects.get(user__email='example@mail.de')
#         token.created_at = timezone.now() - timedelta(days=4)
#         token.save()
#         verify_url = reverse('verify-detail') + f'?code={token.code}'
#         verify_response = self.client.get(verify_url)
#         self.assertEqual(verify_response.status_code, 400)
#         data = {
#             'password': 'newPassword',
#             'repeatPw': 'newPassword',
#             'code': self.token.code
#         }
#         response = self.client.post(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')

#     def test_invalid_method_change_password(self):
#         verify_response = self.client.post(self.url + f'?code={self.token.code}')
#         self.assertEqual(verify_response.status_code, 405)
#         verify_response = self.client.patch(self.url + f'?code={self.token.code}')
#         self.assertEqual(verify_response.status_code, 405)
#         verify_response = self.client.delete(self.url + f'?code={self.token.code}')
#         self.assertEqual(verify_response.status_code, 405)
#         data = {
#             'password': 'newPassword',
#             'repeatPw': 'newPassword',
#             'code': self.token.code
#         }
#         response = self.client.get(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 405)
#         response = self.client.patch(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 405)
#         response = self.client.delete(self.change_url, data, format='json')
#         self.assertEqual(response.status_code, 405)
