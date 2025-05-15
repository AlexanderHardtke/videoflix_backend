from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .test_data import create_video, create_user, create_admin, create_incative_user, create_other_user, invalid_video_pk
from videoflix_db.models import Video
import tempfile
import shutil


class WatchedVideoTests(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.video = create_video(self.admin)
        self.user = create_user()
        self.other_user = create_other_user()
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('watched-list')
        self.video_instance = create_video(self.admin)
        self.client.get(reverse('video-detail', kwargs={'pk': self.video.pk}))

    # def test_get_watched_video_list(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['watched_until'], 0)

    # def test_other_user_get_watched_video_list(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.data[0]['watched_until'], 0)

    #     self.token = Token.objects.create(user=self.other_user)
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 0)

    # def test_unauthorized_get_watched_video_list(self):
    #     client = APIClient()
    #     response = client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_forbidden_get_watched_video_list(self):
    #     user = create_incative_user()
    #     self.token = Token.objects.create(user=user)
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_wrong_method_post_watched_video_list(self):
    #     data = {
    #         'user': 1,
    #         'video': 1,
    #         'watched_until': 0
    #     }
    #     response = self.client.post(self.url, data)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # def test_wrong_method_get_watched_video_detail(self):
    #     response = self.client.get(
    #         reverse('watched-detail', kwargs={'pk': self.video.pk}))
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     data = {
    #         'user': 1,
    #         'video': 1,
    #         'watched_until': 0
    #     }
    #     response = self.client.post(
    #         reverse('watched-detail', kwargs={'pk': self.video.pk}), data)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     response = self.client.delete(
    #         reverse('watched-detail', kwargs={'pk': self.video.pk}))
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_watched_video_detail(self):
        data = {
            'watched_until': 10
        }
        response = self.client.patch(
            reverse('watched-detail', kwargs={'pk': 0}), data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def tearDown(self):
        shutil.rmtree(self._temp_media)
