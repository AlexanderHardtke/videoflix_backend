from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from videoflix_db.models import Video, UserProfil
from .test_data import create_videos, create_admin, create_user, create_incative_user


class VideoUploadTests(APITestCase):

    def setUp(self):
        self.admin = create_admin()
        self.user = create_user()
        self.videos = create_videos(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.admin)
        self.url = reverse('upload-detail')

    def test_upload_Video(self):
        response = ''
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_upload_Video(self):
        response = ''
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_upload_Video(self):
        response = 'nicht angemeldet'
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_upload_Video(self):
        response = 'angemeldeter USer'
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_format_upload_Video(self):
        response = ''
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
