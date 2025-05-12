from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from videoflix_db.models import Video, AbstractUser
from .test_data import create_videos


class VideoTests(APITestCase):

    def setUp(self):
        self.admin = AbstractUser.objects.create_superuser(
            username='staff', password='staffpw', is_staff=True)
        self.user = AbstractUser.objects.create(
            username='testuser', password='testpassword'
        )
        self.videos = create_videos(self.admin)
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.url = reverse('video-list')

    # def test_create_Video(self):
    #     response = ''
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
