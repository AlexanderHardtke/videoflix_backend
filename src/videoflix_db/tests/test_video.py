from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from videoflix_db.models import Video, UserProfil
from .test_data import create_videos, create_admin, create_user


class VideoTests(APITestCase):

    def setUp(self):
        self.admin = create_admin()
        self.user = create_user()
        self.videos = create_videos(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('video-list')

    def test_upload_Video(self):
        response = ''
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
