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