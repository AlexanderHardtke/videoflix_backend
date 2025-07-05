
# class ActivateAccountTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = reverse('registration-detail')
#         settings.EMAIL_CONFIRM_URL = 'https://mocked-url.com'
#         patcher = patch('videoflix_db.api.views.requests.post')
#         self.mock_post = patcher.start()
#         self.addCleanup(patcher.stop)
#         data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword',
#             'repeated_password': 'examplePassword'
#         }
#         self.client.post(self.url, data, format='json')
#         self.token = EmailConfirmationToken.objects.get(user__email='example@mail.de').token

#     def test_activate_account(self):
#         url = reverse('confirm-detail')
#         response = self.client.post(url, {'token': self.token}, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['success'], 'Email confirmed')
#         user = UserProfil.objects.get(email='example@mail.de')
#         self.assertTrue(user.email_confirmed)

#     def test_invalid_token_activate_account(self):
#         url = reverse('confirm-detail')
#         response = self.client.post(url, {'token': 'invalid'}, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')
#         user = UserProfil.objects.get(email='example@mail.de')
#         self.assertFalse(user.email_confirmed)

#     def test_no_token_activate_account(self):
#         url = reverse('confirm-detail')
#         response = self.client.post(url, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')
#         user = UserProfil.objects.get(email='example@mail.de')
#         self.assertFalse(user.email_confirmed)

#     def test_expired_token_activate_account(self):
#         user = UserProfil.objects.get(email='example@mail.de')
#         expired_time = timezone.now() - timedelta(days=2)
#         token = EmailConfirmationToken.objects.create(
#             user=user,
#             token='expired-token-123'
#         )
#         token.created_at = expired_time
#         token.save()
#         url = reverse('confirm-detail')
#         response = self.client.post(url, {'token': token.token}, format='json')
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.data['error'], 'Token is not valid or expired')
#         self.assertFalse(user.email_confirmed)

#     def test_invalid_method_activate_account(self):
#         url = reverse('confirm-detail')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
#         response = self.client.patch(url, {'token': self.token}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# class ProtectedViewTests(APITestCase):

#     def setUp(self):
#         self.user = create_user()
#         self.client = APIClient()
#         self.login_url = reverse('login-detail')
#         self.protected_url = reverse('some-protected-view')

#     def test_access_protected_view_with_valid_cookies(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         self.client.post(self.login_url, login_data, format='json')
#         response = self.client.get(self.protected_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_access_protected_view_without_cookies(self):
#         response = self.client.get(self.protected_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_access_protected_view_with_invalid_access_token(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         self.client.post(self.login_url, login_data, format='json')

#         self.client.cookies['access'] = 'invalid_access_token'
#         response = self.client.get(self.protected_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_access_protected_view_with_expired_access_token_and_valid_refresh(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         response = self.client.post(self.login_url, login_data, format='json')

#         # Manually create an expired access token
#         refresh = RefreshToken.for_user(self.user)
#         refresh.access_token.set_exp(lifetime=timedelta(seconds=-1)) # Expire immediately
#         self.client.cookies['access'] = str(refresh.access_token)

#         response = self.client.get(self.protected_url)
#         # If the backend automatically refreshes, it might be 200, otherwise 401
#         # This depends on how JWT light is configured for automatic refresh.
#         # Assuming it requires an explicit refresh call or returns 401 if access token is expired
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# class RefreshTokenTests(APITestCase):

#     def setUp(self):
#         self.user = create_user()
#         self.client = APIClient()
#         self.login_url = reverse('login-detail')
#         self.refresh_url = reverse('refresh-detail') # Assuming 'refresh-detail' for refresh endpoint

#     def test_refresh_token_success(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         self.client.post(self.login_url, login_data, format='json')

#         response = self.client.post(self.refresh_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('access', response.cookies)
#         self.assertIn('refresh', response.cookies)
#         self.assertTrue(response.cookies['access']['httponly'])
#         self.assertTrue(response.cookies['refresh']['httponly'])

#     def test_refresh_token_without_refresh_cookie(self):
#         response = self.client.post(self.refresh_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_refresh_token_with_invalid_refresh_cookie(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         self.client.post(self.login_url, login_data, format='json')

#         self.client.cookies['refresh'] = 'invalid_refresh_token'
#         response = self.client.post(self.refresh_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_refresh_token_with_expired_refresh_cookie(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         self.client.post(self.login_url, login_data, format='json')

#         # Manually create an expired refresh token
#         refresh = RefreshToken.for_user(self.user)
#         refresh.set_exp(lifetime=timedelta(seconds=-1)) # Expire immediately
#         self.client.cookies['refresh'] = str(refresh)

#         response = self.client.post(self.refresh_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# class LogoutTests(APITestCase):

#     def setUp(self):
#         self.user = create_user()
#         self.client = APIClient()
#         self.login_url = reverse('login-detail')
#         self.logout_url = reverse('logout-detail') # Assuming 'logout-detail' for logout endpoint

#     def test_logout_success(self):
#         login_data = {
#             'email': 'example@mail.de',
#             'password': 'examplePassword'
#         }
#         self.client.post(self.login_url, login_data, format='json')

#         self.assertIn('access', self.client.cookies)
#         self.assertIn('refresh', self.client.cookies)

#         response = self.client.post(self.logout_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['success'], 'Logged out successfully')

#         self.assertIn('access', response.cookies)
#         self.assertIn('refresh', response.cookies)
#         self.assertEqual(response.cookies['access']['max-age'], 0)
#         self.assertEqual(response.cookies['refresh']['max-age'], 0)

#     def test_logout_without_cookies(self):
#         response = self.client.post(self.logout_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['success'], 'Logged out successfully')
#         # Cookies should still be absent or cleared even if not present initially
#         self.assertIn('access', response.cookies)
#         self.assertIn('refresh', response.cookies)
#         self.assertEqual(response.cookies['access']['max-age'], 0)
#         self.assertEqual(response.cookies['refresh']['max-age'], 0)
