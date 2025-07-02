from django.core.files import File
from django.utils import timezone
from django_rq import job
from videoflix_db.models import PasswordForgetToken, EmailConfirmationToken
from .models import Video
import subprocess


def convert_and_save(cmd, video, target, field):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {field} FFmpeg-Fehler:\n{result.stderr}")
            return
        with open(target, 'rb') as f:
            django_file = File(f)
            filename = target.split('/')[-1]
            getattr(video, field).save(filename, django_file, save=True)
    except Exception as e:
        print(f"[CRITICAL] {field} Exception: {str(e)}")


def get_video_duration(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except Exception as e:
        print(f"[ERROR] Duration could not be defined: {e}")
        return None


def create_big_img_from_video(source, video):
    target = source[:-4] + '_big_image.jpg'
    cmd = [
        'ffmpeg', '-y', '-ss', '00:00:02', '-i', source,
        '-vframes', '1', '-vf', 'scale=1920:1080', target
    ]
    convert_and_save(cmd, video, target, 'big_image')


def create_small_img_from_video(source, video):
    target = source[:-4] + '_image.jpg'
    cmd = [
        'ffmpeg', '-y', '-ss', '00:00:02', '-i', source,
        '-vframes', '1', '-vf', 'scale=320:180', target
    ]
    convert_and_save(cmd, video, target, 'image')


def create_small_img_from_img(source, video):
    target = source[:-4] + '_image.jpg'
    source_img = video.big_image.path
    cmd = [
        'ffmpeg', '-y', '-i', source_img,
        '-vf', 'scale=320:180', target
    ]
    convert_and_save(cmd, video, target, 'image')


@job('default')
def convert_720p(video_id, source):
    video = Video.objects.get(id=video_id)
    target = source[:-4] + '_720p.mp4'
    cmd = ['ffmpeg', '-i', source, '-s', '1280x720', '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    convert_and_save(cmd, video, target, 'file720p')


@job('default')
def convert_360p(video_id, source):
    video = Video.objects.get(id=video_id)
    target = source[:-4] + '_360p.mp4'
    cmd = ['ffmpeg', '-i', source, '-s', '640x360', '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    convert_and_save(cmd, video, target, 'file360p')


@job('default')
def convert_240p(video_id, source):
    video = Video.objects.get(id=video_id)
    target = source[:-4] + '_240p.mp4'
    cmd = ['ffmpeg', '-i', source, '-s', '426x240', '-c:v', 'libx264',
           '-crf', '23', '-c:a', 'aac', '-strict', '-2', target]
    convert_and_save(cmd, video, target, 'file240p')


@job('default')
def convert_preview_144p(video_id, source):
    video = Video.objects.get(id=video_id)
    duration = get_video_duration(source)
    if not duration or duration <= 0:
        print(f"[ERROR] Invalid Video playtime: {duration}")
        return
    speed_factor = duration / 10.0
    target = source[:-4] + "_preview144p.mp4"
    cmd = [
        'ffmpeg', '-i', source, '-vf',
        f'setpts=PTS/{speed_factor},scale=-2:144', '-an', '-r',
        '8', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', target
    ]
    convert_and_save(cmd, video, target, 'file_preview144p')


@job('default')
def convert_preview_images(video_id, source):
    video = Video.objects.get(id=video_id)
    if not video.big_image:
        create_big_img_from_video(source, video)
        create_small_img_from_video(source, video)
    else:
        create_small_img_from_img(source, video)


@job('default', result_ttl=0)
def clear_token():
    now = timezone.now()
    expired_pw_tokens = PasswordForgetToken.objects.filter(
        created_at__lt=now - timezone.timedelta(days=1))
    expired_pw_tokens.delete()
    expired_email_tokens = EmailConfirmationToken.objects.filter(
        created_at__lt=now - timezone.timedelta(days=1))
    expired_email_tokens.delete()
