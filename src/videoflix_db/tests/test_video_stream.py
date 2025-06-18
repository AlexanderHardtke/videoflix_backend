from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from videoflix_db.api.utils import generate_video_token, verify_video_token
from rest_framework.test import APIClient
from videoflix_db.models import Video, UserProfil

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
        self.user = UserProfil.objects.create_user(username='tester', password='secret', email='test@example.com')
        self.user.userprofil.email_confirmed = True
        self.user.userprofil.save()

        self.video = Video.objects.create(name='Testvideo')
        self.quality = '720p'
        self.ip = '127.0.0.1'
        setattr(self.video, 'file720p', 'path/to/dummy.mp4')
        self.video.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_access_with_valid_token(self):
        expires = int((timezone.now() + timedelta(minutes=10)).timestamp())
        token = generate_video_token(self.video.id, self.quality, expires, self.ip)

        url = reverse('video-stream', args=[self.video.id, self.quality])
        response = self.client.get(f"{url}?token={token}&expires={expires}", REMOTE_ADDR=self.ip)

        self.assertIn(response.status_code, [200, 206])

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