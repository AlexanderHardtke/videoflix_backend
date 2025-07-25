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


class VideoUploadTests(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.user = create_user()
        self.client = APIClient()
        self.token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('upload-list')
        self.image = SimpleUploadedFile(
            "test.jpg", b"fake image content", content_type="image/jpeg")
        self.video = SimpleUploadedFile(
            "test.mp4", b"fake video content", content_type="video/mp4")

    def test_upload_Video(self):
        initial_count = Video.objects.count()
        data = {
            'name': 'Test Video',
            'video_type': 'training',
            'big_image': self.image,
            'file1080p': self.video
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), initial_count + 1)
        self.assertEqual(response.data['name'], 'Test Video')

    def test_fail_upload_Video(self):
        data = {
            'name': 'Test Video',
            'video_type': 'fail',
            'big_image': 'fail',
            'file1080p': 'fail'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_upload_Video(self):
        client = APIClient()
        data = {
            'name': 'Test Video',
            'video_type': 'training',
            'big_image': self.image,
            'file1080p': self.video
        }
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_upload_Video(self):
        data = {
            'name': 'Test Video',
            'video_type': 'training',
            'big_image': self.image,
            'file1080p': self.video
        }
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_format_upload_Video(self):
        data = {
            'name': 'Test Video',
            'video_type': 'training',
            'file1080p': self.image
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_upload_Video(self):
        video_instance = create_video(self.admin)
        data = {
            'name': 'changed',
            'video_type': 'animals',
            'description_en': 'changedEN',
            'description_de': 'changedDE'
        }
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'changed')
        self.assertEqual(response.data['video_type'], 'animals')
        self.assertEqual(response.data['description_en'], 'changedEN')
        self.assertEqual(response.data['description_de'], 'changedDE')

    def test_wrong_update_upload_Video(self):
        video_instance = create_video(self.admin)
        data = {'video_type': 'error'}
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_update_upload_Video(self):
        video_instance = create_video(self.admin)
        client = APIClient()
        image = SimpleUploadedFile("changed.jpg", b"fake image content", content_type="image/jpeg")
        video = SimpleUploadedFile("changed.mp4", b"fake video content", content_type="video/mp4")
        data = {
            'name': 'changed',
            'video_type': 'animals',
            'big_image': image,
            'file1080p': video
        }
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_update_upload_Video(self):
        video_instance = create_video(self.admin)
        image = SimpleUploadedFile("changed.jpg", b"fake image content", content_type="image/jpeg")
        video = SimpleUploadedFile("changed.mp4", b"fake video content", content_type="video/mp4")
        data = {
            'name': 'changed',
            'video_type': 'animals',
            'big_image': image,
            'file1080p': video
        }
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_found_update_offer(self):
        video_instance = create_video(self.admin)
        image = SimpleUploadedFile("changed.jpg", b"fake image content", content_type="image/jpeg")
        video = SimpleUploadedFile("changed.mp4", b"fake video content", content_type="video/mp4")
        data = {
            'name': 'changed',
            'video_type': 'animals',
            'big_image': image,
            'file1080p': video
        }
        url = reverse('upload-detail', kwargs={'pk': invalid_video_pk})
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_upload_Video(self):
        video_instance = create_video(self.admin)
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_delete_upload_Video(self):
        video_instance = create_video(self.admin)
        client = APIClient()
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_delete_upload_Video(self):
        video_instance = create_video(self.admin)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('upload-detail', kwargs={'pk': video_instance.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_found_delete_upload_Video(self):
        video_instance = create_video(self.admin)
        url = reverse('upload-detail', kwargs={'pk': invalid_video_pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        shutil.rmtree(self._temp_media)


class VideoTests(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.video = create_video(self.admin)
        self.user = create_user()
        self.client = APIClient()
        login_url = reverse('login-detail')
        login_data = {
            'email': 'example@mail.de',
            'password': 'examplePassword'
        }
        self.client.post(login_url, login_data, format='json')
        self.url = reverse('video-list')

    def test_get_video_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_get_video_list(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unverified_get_video_list(self):
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

    def test_get_video_single(self):
        response = self.client.get(reverse('video-detail', kwargs={'pk': self.video.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'exampleName')
        self.assertIn('id', response.data)

    def test_unauthorized_get_video_single(self):
        client = APIClient()
        response = client.get(reverse('video-detail', kwargs={'pk': self.video.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unverified_get_video_single(self):
        client = APIClient()
        create_incative_user()
        login_url = reverse('login-detail')
        login_data = {
            'email': 'inactiveuser@mail.de',
            'password': 'examplePassword'
        }
        self.client.post(login_url, login_data, format='json')
        response = client.get(reverse('video-detail', kwargs={'pk': self.video.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_found_get_video_single(self):
        response = self.client.get(reverse('video-detail', kwargs={'pk': invalid_video_pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_methods_get_video_list(self):
        image = SimpleUploadedFile("changed.jpg", b"fake image content", content_type="image/jpeg")
        video = SimpleUploadedFile("changed.mp4", b"fake video content", content_type="video/mp4")
        data = {
            'name': 'Test Video',
            'video_type': 'training',
            'big_image': image,
            'file1080p': video
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_wrong_methods_get_video_single(self):
        image = SimpleUploadedFile("changed.jpg", b"fake image content", content_type="image/jpeg")
        video = SimpleUploadedFile("changed.mp4", b"fake video content", content_type="video/mp4")
        data = {
            'name': 'Test Video',
            'video_type': 'training',
            'big_image': image,
            'file1080p': video
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def tearDown(self):
        shutil.rmtree(self._temp_media)
