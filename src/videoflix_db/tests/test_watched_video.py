from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from videoflix_db.models import Video, AbstractUser, UserProfil


class WatchedVideoTests(APITestCase):

    def setUp(self):
        self.user = AbstractUser.objects.create(
            username='testuser', password='testpassword'
        )
        self.client = APIClient()
        self.url = reverse('registration-detail')
