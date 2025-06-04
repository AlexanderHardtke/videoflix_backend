from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import secrets


class UserProfil(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    preferred_size = models.CharField(max_length=5, default='')
    sound_volume = models.CharField(max_length=3, default=50)

    def generate_confirmation_token(self):
        self.confirmation_token = secrets.token_hex(32)
        self.token_created_at = timezone.now()
        self.save()


class EmailConfirmationToken(models.Model):
    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).days >= 1


class PasswordForgetToken(models.Model):
    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).days >= 1


class Video(models.Model):
    video_types = [
        ('animals', 'Animals'),
        ('nature', 'Nature'),
        ('training', 'Training'),
        ('tutorials', 'Tutorials')
    ]
    name = models.CharField(max_length=50, default='')
    descriptionEN = models.TextField(max_length=1000, default='')
    descriptionDE = models.TextField(max_length=1000, default='')
    type = models.CharField(
        max_length=50, choices=video_types, default='movies')
    image = models.FileField(max_length=99, blank=True,
                             null=True, upload_to='images/')
    file1080p = models.FileField(
        max_length=99, blank=True, upload_to='movies/')
    file720p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file360p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file240p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    filePreview144p = models.FileField(max_length=99, blank=True, upload_to='previews/')
    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False)


class WatchedVideo(models.Model):
    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_until = models.IntegerField(default=0)
