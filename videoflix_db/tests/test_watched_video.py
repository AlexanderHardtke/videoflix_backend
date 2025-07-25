from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .test_data import create_video, create_user, create_admin, create_incative_user, create_other_user, invalid_video_pk
from videoflix_db.models import Video, WatchedVideo
import tempfile
import shutil


class WatchedVideoTests(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.video = create_video(self.admin)
        self.user = create_user()
        self.client = APIClient()
        self.other_user = create_other_user()
        login_url = reverse('login-detail')
        login_data = {
            'email': 'example@mail.de',
            'password': 'examplePassword'
        }
        self.client.post(login_url, login_data, format='json')
        self.watched = WatchedVideo.objects.create(
            video=self.video, user=self.user, watched_until=0)
        self.url = reverse('watched-detail', kwargs={'pk': self.watched.pk})

    def test_get_watched_video_list(self):
        url = reverse('video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['list'][0]['watched_until'], 0)

    def test_other_user_get_watched_video_list(self):
        url = reverse('video-list')
        response = self.client.get(url)
        self.assertEqual(response.data['list'][0]['watched_until'], 0)
        client = APIClient()
        login_url = reverse('login-detail')
        login_data = {
            'email': 'other@mail.de',
            'password': 'otherPassword'
        }
        client.post(login_url, login_data, format='json')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['list'][0]['watched_until'], None)

    def test_unauthorized_get_watched_video_list(self):
        client = APIClient()
        url = reverse('video-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unverified_get_watched_video_list(self):
        client = APIClient()
        create_incative_user()
        login_url = reverse('login-detail')
        login_data = {
            'email': 'inactiveuser@mail.de',
            'password': 'examplePassword'
        }
        self.client.post(login_url, login_data, format='json')
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_method_post_watched_video_list(self):
        data = {
            'user': 1,
            'video': 1,
            'watched_until': 0
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_watched_video_detail(self):
        response = self.client.patch(self.url, {"watched_until": 42}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['watched_until'], 42)

    def test_wrong_patch_watched_video_detail(self):
        response = self.client.patch(
            self.url, {"watched_until": "Not a Number"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_patch_watched_video_detail(self):
        client = APIClient()
        response = client.patch(self.url, {"watched_until": 42}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_hide_unverified_patch_watched_video_detail(self):
        client = APIClient()
        create_incative_user()
        login_url = reverse('login-detail')
        login_data = {
            'email': 'inactiveuser@mail.de',
            'password': 'examplePassword'
        }
        self.client.post(login_url, login_data, format='json')
        response = client.patch(self.url, {"watched_until": 42}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_found_patch_watched_video_detail(self):
        url = reverse('watched-detail', kwargs={'pk': invalid_video_pk})
        response = self.client.patch(url, {"watched_until": 42}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_method_get_watched_video_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = {
            'user': 1,
            'video': 1,
            'watched_until': 0
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def tearDown(self):
        shutil.rmtree(self._temp_media)
