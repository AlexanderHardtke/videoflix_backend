from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth.models import AbstractUser


class UserProfil(AbstractUser):
    preferredSize = models.CharField(max_length=5, default='')
    

class Video(models.Model):
    created_at = models.DateField(default=date.today)

# class WatchedVideo(models.Model):
#     One-models.ManyToManyField("app.Model", verbose_name=_(""))