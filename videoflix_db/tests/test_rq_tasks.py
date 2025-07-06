import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from .test_data import create_admin, create_video
from videoflix_db.tasks import (
    convert_720p, convert_360p, convert_240p, convert_preview_144p,
    convert_preview_images
)


class VideoConversionTaskTests(TestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media
        self.admin = create_admin()
        self.video = create_video(self.admin)
        movie_dir = os.path.join(self._temp_media, 'movies')
        os.makedirs(movie_dir, exist_ok=True)
        source_file = os.path.join(movie_dir, 'test_1080p.mp4')
        with open(source_file, 'wb') as f:
            f.write(b'\x00' * 1024)
        self.video.file1080p.name = os.path.relpath(source_file, self._temp_media)
        self.video.save()
        self.source_path = self.video.file1080p.path

    @patch('videoflix_db.tasks.subprocess.run')
    def test_video_conversion_tasks_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        base, ext = os.path.splitext(self.source_path)
        dummy_720p_path = base + '_720p.mp4'
        dummy_360p_path = base + '_360p.mp4'
        dummy_240p_path = base + '_240p.mp4'
        for path in [dummy_720p_path, dummy_360p_path, dummy_240p_path]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(b'\x00')
        convert_720p(self.video.id, self.source_path)
        convert_360p(self.video.id, self.source_path)
        convert_240p(self.video.id, self.source_path)
        self.video.refresh_from_db()
        self.assertTrue('_720p' in self.video.file720p.name and self.video.file720p.name.endswith('.mp4'))
        self.assertTrue('_360p' in self.video.file360p.name and self.video.file360p.name.endswith('.mp4'))
        self.assertTrue('_240p' in self.video.file240p.name and self.video.file240p.name.endswith('.mp4'))
        self.assertEqual(mock_run.call_count, 3)
        mock_run.reset_mock()

    @patch('videoflix_db.tasks.subprocess.run')
    @patch('videoflix_db.tasks.get_video_duration', return_value=120)
    def test_convert_preview_144p_success(self, mock_get_duration, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        base, _ = os.path.splitext(self.source_path)
        dummy_144p_path = base + '_preview144p.mp4'
        os.makedirs(os.path.dirname(dummy_144p_path), exist_ok=True)
        with open(dummy_144p_path, 'wb') as f:
            f.write(b'\x00')
        convert_preview_144p(self.video.id, self.source_path)
        self.video.refresh_from_db()
        self.assertIn('_preview144p', self.video.file_preview144p.name)
        self.assertTrue(self.video.file_preview144p.name.endswith('.mp4'))
        self.assertEqual(mock_run.call_count, 1)

    @patch('videoflix_db.tasks.subprocess.run')
    def test_convert_preview_images_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        base, _ = os.path.splitext(self.source_path)
        dummy_big_image = base + '_big_image.jpg'
        dummy_image = base + '_image.jpg'
        os.makedirs(os.path.dirname(dummy_big_image), exist_ok=True)
        with open(dummy_big_image, 'wb') as f:
            f.write(b'\x00')
        with open(dummy_image, 'wb') as f:
            f.write(b'\x00')
        convert_preview_images(self.video.id, self.source_path)
        self.video.refresh_from_db()
        self.assertTrue(self.video.big_image and self.video.image)
        self.assertIn('_big_image', self.video.big_image.name)
        self.assertIn('_image', self.video.image.name)
        self.assertTrue(self.video.big_image.name.endswith('.jpg'))
        self.assertTrue(self.video.image.name.endswith('.jpg'))
        self.assertEqual(mock_run.call_count, 2)

    @patch('videoflix_db.tasks.subprocess.run')
    @patch('videoflix_db.tasks.get_video_duration', return_value=0)
    def test_convert_preview_144p_invalid_duration(self, mock_get_duration, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        convert_preview_144p(self.video.id, self.source_path)
        self.video.refresh_from_db()
        self.assertFalse(self.video.file_preview144p)
        mock_run.reset_mock()

    def tearDown(self):
        shutil.rmtree(self._temp_media)
