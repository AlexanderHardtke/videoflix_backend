from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .test_data import create_videos, create_admin, create_user, invalid_video_pk


class VideoUploadTests(APITestCase):

    def setUp(self):
        self.admin = create_admin()
        self.user = create_user()
        self.video = create_videos(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.admin)
        self.url = reverse('upload-detail')

    def test_upload_Video(self):
        data = create_videos(self.admin)
        response = self.admin.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fail_upload_Video(self):
        data = {
            'name': 'exampleName',
            'type': '',
            'image': '',
            'file1080p': ''
        }
        response = self.admin.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_upload_Video(self):
        data = create_videos()
        response = self.admin.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_upload_Video(self):
        data = create_videos(self.user)
        response = self.admin.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_format_upload_Video(self):
        data = {
            'name': 'exampleName',
            'type': 'animals',
            'image': 'src/media/images/Alex.PNG',
            'file1080p': 'src/media/movies/wrong_format.mp3'
        }
        response = self.admin.post(self.url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
    def test_update_upload_Video(self):
        data = {
            'name': 'exampleName',
            'type': 'animals',
            'image': 'src/media/images/Alex.PNG',
            'file1080p': 'src/media/movies/wrong_format.mp3'
        }
        url = reverse('upload-detail', kwargs={'pk': self.user_video[0].pk})

    def test_patch_offer(self):
        url = reverse('upload-detail', kwargs={'pk': self.user_video[0].pk})
        response = self.client.patch(url, patched_video_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_found_update_offer(self):
        url = reverse('upload-detail', kwargs={'pk': invalid_video_pk})
        response = self.client.patch(url, patched_video_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_upload_Video(self):
        url = reverse('upload-detail', kwargs={'pk': self.user_offers[0].pk})
        data = create_videos(self.user)


class VideoTests(APITestCase):

    def setUp(self):
        self.admin = create_admin()
        self.user = create_user()
        self.video = create_videos(self.admin)
        self.video2 = create_videos(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.admin)
        self.url_list = reverse('video-list')
        self.url = reverse('video-detail')

    def test_get_video_list(self):
        response = self.admin.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_get_video_list(self):
        response = self.client.get(self.url_list, {'unvalid_key': 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_get_video_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_wrong_methods_get_video_list(self):
    #     response = self.client.post(self.url_list)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_video_single(self):
        response = self.admin.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_get_video_single(self):
        response = self.client.get(self.url, {'unvalid_key': 100})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_get_video_single(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #     def test_wrong_methods_get_video_list(self):
    #     response = self.client.post(self.url_list)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class WatchedVideoTests(APITestCase):

    def setUp(self):
        self.admin = create_admin()
        self.user = create_user()
        self.videos = create_videos(self.admin)
        self.video2 = create_videos(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.admin)
        self.url_list = reverse('video-list')
        self.url = reverse('video-detail')
