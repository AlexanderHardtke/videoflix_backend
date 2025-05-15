from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from videoflix_db.models import Video, AbstractUser, UserProfil


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
