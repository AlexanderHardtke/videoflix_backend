from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .test_data import create_video, create_admin, create_user, invalid_video_pk
from videoflix_db.models import Video
import tempfile
import shutil


class VideoUploadTests(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.user = create_user()
        self.video = create_video(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('upload-list')
        self.image = SimpleUploadedFile("test.jpg", b"fake image content", content_type="image/jpeg")
        self.video = SimpleUploadedFile("test.mp4", b"fake video content", content_type="video/mp4")

    def test_upload_Video(self):
        initial_count = Video.objects.count()
        data = {
            'name': 'Test Video',
            'type': 'training',
            'image': self.image,
            'file1080p': self.video,
            'uploaded_by': self.admin.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), initial_count + 1)
        self.assertEqual(response.data['name'], 'Test Video')

    def test_fail_upload_Video(self):
        data = {
            'name': 'Test Video',
            'type': 'fail',
            'image': 'fail',
            'file1080p': 'fail',
            'uploaded_by': self.admin.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_upload_Video(self):
        client = APIClient()
        data = {
            'name': 'Test Video',
            'type': 'training',
            'image': self.image,
            'file1080p': self.video,
            'uploaded_by': self.admin.id
        }
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_upload_Video(self):
        data = {
            'name': 'Test Video',
            'type': 'training',
            'image': self.image,
            'file1080p': self.video,
            'uploaded_by': self.admin.id
        }
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_format_upload_Video(self):
        data = {
            'name': 'Test Video',
            'type': 'training',
            'image': self.image,
            'file1080p': self.image,
            'uploaded_by': self.admin.id
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_upload_Video(self):
        image = SimpleUploadedFile("changed.jpg", b"fake image content", content_type="image/jpeg")
        video = SimpleUploadedFile("changed.mp4", b"fake video content", content_type="video/mp4")
        data = {
            'name': 'changed',
            'type': 'animals',
            'image': image,
            'file1080p': video
        }
        url = reverse('upload-detail', kwargs={'pk': self.video.pk})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'changed')

#     def test_patch_offer(self):
#         url = reverse('upload-detail', kwargs={'pk': self.user_video[0].pk})
#         response = self.client.patch(url, patched_video_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_not_found_update_offer(self):
#         url = reverse('upload-detail', kwargs={'pk': invalid_video_pk})
#         response = self.client.patch(url, patched_video_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_delete_upload_Video(self):
#         url = reverse('upload-detail', kwargs={'pk': self.user_offers[0].pk})
#         data = create_videos(self.user)

    def tearDown(self):
        shutil.rmtree(self._temp_media)


# class VideoTests(APITestCase):

#     def setUp(self):
#         self.admin = create_admin()
#         self.user = create_user()
#         self.video = create_videos(self.admin)
#         self.video2 = create_videos(self.admin)
#         self.client = APIClient()
#         self.token = Token.objects.create(user=self.admin)
#         self.url_list = reverse('video-list')
#         self.url = reverse('video-detail')

#     def test_get_video_list(self):
#         response = self.admin.get(self.url_list)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_unauthorized_get_video_list(self):
#         response = self.client.get(self.url_list, {'unvalid_key': 100})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_unauthorized_get_video_list(self):
#         response = self.client.get(self.url_list)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     # def test_wrong_methods_get_video_list(self):
#     #     response = self.client.post(self.url_list)
#     #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_get_video_single(self):
#         response = self.admin.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_unauthorized_get_video_single(self):
#         response = self.client.get(self.url, {'unvalid_key': 100})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_unauthorized_get_video_single(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     #     def test_wrong_methods_get_video_list(self):
#     #     response = self.client.post(self.url_list)
#     #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# class WatchedVideoTests(APITestCase):

#     def setUp(self):
#         self.admin = create_admin()
#         self.user = create_user()
#         self.videos = create_videos(self.admin)
#         self.video2 = create_videos(self.admin)
#         self.client = APIClient()
#         self.token = Token.objects.create(user=self.admin)
#         self.url_list = reverse('video-list')
#         self.url = reverse('video-detail')
