from .tasks import convert_720p, convert_360p, convert_240p
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        convert_720p.delay(instance.file1080p.path)
        convert_360p.delay(instance.file1080p.path)
        convert_240p.delay(instance.file1080p.path)

@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):
    if instance.file1080p:
        if os.path.isfile(instance.file1080p.path):
            os.remove(instance.file1080p.path)
