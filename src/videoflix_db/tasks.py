from django.conf import settings
from django.utils import timezone
from django_rq import job
from videoflix_db.models import PasswordForgetToken, EmailConfirmationToken
from .models import Video
import subprocess


def convert_and_save(video_id, source, resolution, dimensions):
    target = source[:-4] + f"_{resolution}.mp4"
    cmd = ['ffmpeg', '-i', source, '-s', dimensions, '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {resolution} FFmpeg-Fehler:\n{result.stderr}")
            return
        video = Video.objects.get(id=video_id)
        relative_path = target.replace(settings.MEDIA_ROOT + '/', '')
        setattr(video, f'file'+resolution, relative_path)
        video.save(update_fields=[f'file'+resolution])
    except Exception as e:
        print(f"[CRITICAL] {resolution} Ausnahme: {str(e)}")


@job('queue_720p')
def convert_720p(video_id, source):
    convert_and_save(video_id, source, '720p', '1280x720')


@job('queue_360p')
def convert_360p(video_id, source):
    convert_and_save(video_id, source, '360p', '640x360')


@job('queue_240p')
def convert_240p(video_id, source):
    convert_and_save(video_id, source, '240p', '426x240')

@job('queue_token')
def clear_token():
    now = timezone.now()
    expired_pw_tokens = PasswordForgetToken.objects.filter(created_at__lt=now - timezone.timedelta(days=1))
    expired_pw_tokens.delete()
    expired_email_tokens = EmailConfirmationToken.objects.filter(created_at__lt=now - timezone.timedelta(days=1))
    expired_email_tokens.delete()
