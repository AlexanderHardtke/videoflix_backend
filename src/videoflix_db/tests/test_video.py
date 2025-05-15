from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .test_data import create_video, create_user, create_admin, create_incative_user, invalid_video_pk
from videoflix_db.models import Video
import tempfile
import shutil

class VideoTests(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.video = create_video(self.admin)
        self.video2 = create_video(self.admin)
        self.user = create_user()
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url_list = reverse('video-list')
        self.url = reverse('video-detail', kwargs={'pk': self.video.pk})

    def test_get_video_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_get_video_list(self):
        client = APIClient()
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_get_video_list(self):
        user = create_incative_user()
        client = APIClient()
        self.token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_wrong_methods_get_video_list(self):
    #     response = self.client.post(self.url_list)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_video_single(self):
    #     response = self.admin.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_unauthorized_get_video_single(self):
    #     response = self.client.get(self.url, {'unvalid_key': 100})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_unauthorized_get_video_single(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #     def test_wrong_methods_get_video_list(self):
    #     response = self.client.post(self.url_list)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        shutil.rmtree(self._temp_media)
