from django.urls import reverse
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from videoflix_db.api.utils import generate_video_token, verify_video_token
from .test_data import create_video, create_user, create_admin, create_incative_user, invalid_video_pk
from rest_framework.test import APIClient
from rest_framework import status
from videoflix_db.models import Video
import tempfile
import shutil


class TokenTests(TestCase):

    def setUp(self):
        self.video_id = 1
        self.quality = '720p'
        self.ip = '127.0.0.1'
        self.now = int(timezone.now().timestamp())
        self.future = self.now + 600

    def test_valid_token(self):
        token = generate_video_token(self.video_id, self.quality, self.future, self.ip)
        is_valid = verify_video_token(self.video_id, self.quality, token, self.future, self.ip)
        self.assertTrue(is_valid)

    def test_invalid_ip(self):
        token = generate_video_token(self.video_id, self.quality, self.future, '1.2.3.4')
        is_valid = verify_video_token(self.video_id, self.quality, token, self.future, '5.6.7.8')
        self.assertFalse(is_valid)

    def test_expired_token(self):
        expired_time = self.now - 10
        token = generate_video_token(self.video_id, self.quality, expired_time, self.ip)
        is_valid = verify_video_token(self.video_id, self.quality, token, expired_time, self.ip)
        self.assertFalse(is_valid)

    def test_tampered_token(self):
        token = generate_video_token(self.video_id, self.quality, self.future, self.ip)
        tampered_token = token[:-1] + ('A' if token[-1] != 'A' else 'B')
        is_valid = verify_video_token(self.video_id, self.quality, tampered_token, self.future, self.ip)
        self.assertFalse(is_valid)


class VideoStreamTests(TestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.video = create_video(self.admin)
        self.user = create_user()
        self.client = APIClient()
        self.quality = '1080p'
        self.ip = '127.0.0.1'

    def test_access_with_valid_token_full_content(self):
        expires = int((timezone.now() + timedelta(minutes=10)).timestamp())
        token = generate_video_token(self.video.id, self.quality, expires, self.ip)
        url = reverse('video-stream', args=[self.video.id, self.quality])
        response = self.client.get(f"{url}?token={token}&expires={expires}", REMOTE_ADDR=self.ip)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_access_with_valid_token_range_request(self):
        expires = int((timezone.now() + timedelta(minutes=10)).timestamp())
        token = generate_video_token(self.video.id, self.quality, expires, self.ip)
        url = reverse('video-stream', args=[self.video.id, self.quality])
        response = self.client.get(
            f"{url}?token={token}&expires={expires}", 
            REMOTE_ADDR=self.ip,
            HTTP_RANGE='bytes=0-1023'
        )
        self.assertIn('Content-Range', response)
        self.assertEqual(response['Accept-Ranges'], 'bytes')
        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)

    def test_access_with_invalid_token(self):
        expires = int((timezone.now() + timedelta(minutes=10)).timestamp())
        token = "invalidtoken"
        url = reverse('video-stream', args=[self.video.id, self.quality])
        response = self.client.get(f"{url}?token={token}&expires={expires}", REMOTE_ADDR=self.ip)
        self.assertEqual(response.status_code, 401)

    def test_access_with_expired_token(self):
        expires = int((timezone.now() - timedelta(minutes=1)).timestamp())
        token = generate_video_token(self.video.id, self.quality, expires, self.ip)
        url = reverse('video-stream', args=[self.video.id, self.quality])
        response = self.client.get(f"{url}?token={token}&expires={expires}", REMOTE_ADDR=self.ip)
        self.assertEqual(response.status_code, 401)

    def tearDown(self):
        shutil.rmtree(self._temp_media)