from django.conf import settings
from django.utils import timezone
from django_rq import job
from videoflix_db.models import PasswordForgetToken, EmailConfirmationToken
from .models import Video
import subprocess


def convert_and_save(cmd, video, target, resolution):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {resolution} FFmpeg-Fehler:\n{result.stderr}")
            return
        relative_path = target.replace(settings.MEDIA_ROOT + '/', '')
        setattr(video, f'file'+resolution, relative_path)
        video.save(update_fields=[f'file'+resolution])
    except Exception as e:
        print(f"[CRITICAL] {resolution} Ausnahme: {str(e)}")


def get_video_duration(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[ERROR] Dauer konnte nicht ermittelt werden: {e}")
        return None


def convert_preview_image(video, source, scale, name):
    preview_target = source[:-4] + name
    cmd = [
        'ffmpeg', '-ss', '00:00:01', '-i', source, '-vframes',
        '1', '-vf', scale, preview_target
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Screenshot-FFmpeg-Fehler:\n{result.stderr}")
            return
        relative_image_path = preview_target.replace(
            settings.MEDIA_ROOT + '/', '')
        video.image.name = relative_image_path
        video.save(update_fields=['image'])
    except Exception as e:
        print(f"[CRITICAL] Screenshot konnte nicht erstellt werden: {e}")


@job('queue_720p')
def convert_720p(video_id, source):
    video = Video.objects.get(id=video_id)
    target = source[:-4] + '_720p.mp4'
    cmd = ['ffmpeg', '-i', source, '-s', '1280x720', '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    convert_and_save(cmd, video, target, '720p')


@job('queue_360p')
def convert_360p(video_id, source):
    video = Video.objects.get(id=video_id)
    target = source[:-4] + '_360p.mp4'
    cmd = ['ffmpeg', '-i', source, '-s', '640x360', '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    convert_and_save(cmd, video, target, '360p')


@job('queue_240p')
def convert_240p(video_id, source):
    video = Video.objects.get(id=video_id)
    target = source[:-4] + '_240p.mp4'
    cmd = ['ffmpeg', '-i', source, '-s', '426x240', '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    convert_and_save(cmd, video, target, '240p')


@job('queue_preview144p')
def convert_preview_144p(video_id, source):
    video = Video.objects.get(id=video_id)
    duration = get_video_duration(source)
    if not duration or duration <= 0:
        print(f"[ERROR] Ungültige Videodauer: {duration}")
        return
    speed_factor = duration / 10.0
    target = source[:-4] + "_preview144p.mp4"
    cmd = [
        'ffmpeg', '-i', source, '-vf',
        f'setpts=PTS/{speed_factor},scale=-2:144', '-an', '-r',
        '8', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', target
    ]
    convert_and_save(cmd, video, target, 'Preview144p')
    if not video.image:
        convert_preview_image(video, source, 'scale=-2:144', '_preview')
    if not video.bigImage:
        convert_preview_image(video, source, 'scale=1920:1080', '_big')


@job('queue_token')
def clear_token():
    now = timezone.now()
    expired_pw_tokens = PasswordForgetToken.objects.filter(
        created_at__lt=now - timezone.timedelta(days=1))
    expired_pw_tokens.delete()
    expired_email_tokens = EmailConfirmationToken.objects.filter(
        created_at__lt=now - timezone.timedelta(days=1))
    expired_email_tokens.delete()
