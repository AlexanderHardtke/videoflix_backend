from .tasks import convert_720p, convert_360p, convert_240p, convert_preview_144p
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        convert_720p.delay(instance.id, instance.file1080p.path)
        convert_360p.delay(instance.id, instance.file1080p.path)
        convert_240p.delay(instance.id, instance.file1080p.path)
        convert_preview_144p.delay(instance.id, instance.file1080p.path)

@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):
    fields = ['file1080p', 'file720p', 'file360p', 'file240p', 'preview144p']
    for field in fields:
        file_field = getattr(instance, field)
        if file_field and os.path.isfile(file_field.path):
            os.remove(file_field.path)
