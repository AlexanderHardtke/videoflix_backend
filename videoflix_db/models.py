from django.db import models
from authemail.models import EmailUserManager, EmailAbstractUser


class UserProfil(EmailAbstractUser):
    username = models.CharField(max_length=75, unique=False, blank=True)
    sound_volume = models.IntegerField(default=50)
    objects = EmailUserManager()


class Video(models.Model):
    VIDEO_TYPE_CHOICES = [
    ('animals', 'Animals'), ('nature', 'Nature'),
    ('training', 'Training'), ('tutorials', 'Tutorials'),
]
    name = models.CharField(max_length=50, default='')
    description_en = models.TextField(max_length=1000, default='')
    description_de = models.TextField(max_length=1000, default='')
    video_type = models.CharField(max_length=50, choices=VIDEO_TYPE_CHOICES, default='movies')
    big_image = models.FileField(max_length=99, blank=True,null=True, upload_to='movies/')
    image = models.FileField(max_length=99, blank=True,null=True, upload_to='movies/')
    file1080p = models.FileField(max_length=99, upload_to='movies/')
    file720p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file360p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file240p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    file_preview144p = models.FileField(max_length=99, blank=True, upload_to='movies/')
    duration = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, editable=False)


class WatchedVideo(models.Model):
    user = models.ForeignKey(UserProfil, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_until = models.IntegerField(default=0)
