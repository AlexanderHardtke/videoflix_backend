from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth.models import AbstractUser


class UserProfil(AbstractUser):
    preferred_size = models.CharField(max_length=5, default='')
    sound_volume = models.CharField(max_length=3, default=50)
    

class Video(models.Model):
    created_at = models.DateField(default=date.today)
    name = models.CharField(max_length=50, default='')
    image = models.FileField(max_length=99, blank=True, null=True, upload_to='images/')
    file1080p = models.FileField(max_length=99, blank=True, upload_to='images/')
    file720p = models.FileField(max_length=99, blank=True, upload_to='images/')
    file360p = models.FileField(max_length=99, blank=True, upload_to='images/')
    file120p = models.FileField(max_length=99, blank=True, upload_to='images/')


class WatchedVideo(models.Model):
    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_until = models.DurationField()
