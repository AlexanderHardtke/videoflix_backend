from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser


class UserProfil(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    preferred_size = models.CharField(max_length=5, default='')
    sound_volume = models.CharField(max_length=3, default=50)
    

class Video(models.Model):
    video_types = [
        ('animals', 'Animals'),
        ('nature', 'Nature'),
        ('training', 'Training'),
        ('tutorials', 'Tutorials')
    ]
    name = models.CharField(max_length=50, default='')
    type = models.CharField(max_length=50, choices=video_types, default='movies')
    image = models.FileField(max_length=99, blank=True, null=True, upload_to='images/')
    file1080p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file720p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file360p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file120p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False)
    uploaded_by = models.ForeignKey(UserProfil, on_delete=models.CASCADE, related_name='videos',  null=True, blank=True)


class WatchedVideo(models.Model):
    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_until = models.IntegerField(default=0)
