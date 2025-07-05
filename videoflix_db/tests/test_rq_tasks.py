# from unittest.mock import patch, MagicMock
# from django.test import TestCase
# from django.conf import settings
# from django.utils import timezone
# from .test_data import create_admin, create_video, create_user
# from videoflix_db.tasks import (
#     convert_720p, convert_360p, convert_240p, convert_preview_144p,
#     convert_preview_images, clear_token
# )
# from videoflix_db.models import EmailConfirmationToken, PasswordForgetToken
# import tempfile
# import shutil


# class VideoConversionTaskTests(TestCase):

#     def setUp(self):
#         self._temp_media = tempfile.mkdtemp()
#         settings.MEDIA_ROOT = self._temp_media
#         self.admin = create_admin()
#         self.video = create_video(self.admin)
#         self.source_path = self.video.file1080p.path

#     @patch('videoflix_db.tasks.subprocess.run')
#     def test_video_conversion_tasks_success(self, mock_run):
#         mock_run.return_value = MagicMock(returncode=0, stdout="")
#         convert_720p(self.video.id, self.source_path)
#         convert_360p(self.video.id, self.source_path)
#         convert_240p(self.video.id, self.source_path)
#         self.video.refresh_from_db()
#         self.assertTrue(self.video.file720p.name.endswith('_720p.mp4'))
#         self.assertTrue(self.video.file360p.name.endswith('_360p.mp4'))
#         self.assertTrue(self.video.file240p.name.endswith('_240p.mp4'))
#         self.assertEqual(mock_run.call_count, 3)
#         mock_run.reset_mock()

#     @patch('videoflix_db.tasks.subprocess.run')
#     @patch('videoflix_db.tasks.get_video_duration', return_value=120)
#     def test_convert_preview_144p_success(self, mock_get_duration, mock_run):
#         mock_run.return_value = MagicMock(returncode=0, stdout="")
#         convert_preview_144p(self.video.id, self.source_path)
#         self.video.refresh_from_db()
#         self.assertTrue(self.video.file_preview144p.name.endswith('_preview144p.mp4'))
#         self.assertEqual(mock_run.call_count, 1)

#     @patch('videoflix_db.tasks.subprocess.run')
#     def test_convert_preview_images_success(self, mock_run):
#         mock_run.return_value = MagicMock(returncode=0, stdout="")
#         convert_preview_images(self.video.id, self.source_path)
#         self.video.refresh_from_db()
#         self.assertTrue(self.video.big_image and self.video.image)
#         self.assertEqual(mock_run.call_count, 2)

#     @patch('videoflix_db.tasks.subprocess.run')
#     @patch('videoflix_db.tasks.get_video_duration', return_value=0)
#     def test_convert_preview_144p_invalid_duration(self, mock_get_duration, mock_run):
#         mock_run.return_value = MagicMock(returncode=0, stdout="")
#         convert_preview_144p(self.video.id, self.source_path)
#         self.video.refresh_from_db()
#         self.assertFalse(self.video.file_preview144p)
#         mock_run.reset_mock()

#     def tearDown(self):
#         shutil.rmtree(self._temp_media)


# class TokenCleanupTaskTests(TestCase):

#     def setUp(self):
#         self.user = create_user()
#         self.expired_time = timezone.now() - timezone.timedelta(days=2)
#         self.unexpired_time = timezone.now() - timezone.timedelta(hours=1)
        

    
#     def test_clear_token_deletes_expired_tokens(self):
#         pw_token = PasswordForgetToken.objects.create(user=self.user, token='abc')
#         email_token = EmailConfirmationToken.objects.create(user=self.user, token='xyz')
#         self.assertTrue(PasswordForgetToken.objects.filter(id=pw_token.id).exists())
#         self.assertTrue(EmailConfirmationToken.objects.filter(id=email_token.id).exists())
#         pw_token.created_at = self.expired_time
#         pw_token.save()
#         email_token.created_at = self.expired_time
#         email_token.save()
#         clear_token()
#         self.assertFalse(PasswordForgetToken.objects.filter(id=pw_token.id).exists())
#         self.assertFalse(EmailConfirmationToken.objects.filter(id=email_token.id).exists())

#     def test_token_not_deletes_unexpired_tokens(self):
#         pw_token = PasswordForgetToken.objects.create(user=self.user, token='abc')
#         email_token = EmailConfirmationToken.objects.create(user=self.user, token='xyz')
#         pw_token.created_at = self.unexpired_time
#         pw_token.save()
#         email_token.created_at = self.unexpired_time
#         email_token.save()
#         clear_token()
#         self.assertTrue(PasswordForgetToken.objects.filter(id=pw_token.id).exists())
#         self.assertTrue(EmailConfirmationToken.objects.filter(id=email_token.id).exists())