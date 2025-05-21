import subprocess
from django_rq import job
from .models import Video
from django.conf import settings


@job('queue_720p')
def convert_720p(video_id, source):
    target = source[:-4] + '_720p.mp4'
    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', '1280x720',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]
    run = subprocess.run(cmd, shell=True, capture_output=True)
    try:
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode != 0:
            print(f"[ERROR] 720p-FFmpeg-Fehler:\n{run.stderr}")
        else:
            print("[SUCCESS] 720p-Konvertierung abgeschlossen!")
            video = Video.objects.get(id=video_id)
            relative_path = target.replace(settings.MEDIA_ROOT + '/', '')
            video.file720p.name = relative_path
            video.save(update_fields=['file720p'])
    except Exception as e:
        print(f"[CRITICAL] 720p-Ausnahme: {str(e)}")


@job('queue_360p')
def convert_360p(video_id, source):
    target = source[:-4] + '_360p.mp4'
    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', '640x360',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]
    run = subprocess.run(cmd, shell=True, capture_output=True)
    try:
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode != 0:
            print(f"[ERROR] 360p-FFmpeg-Fehler:\n{run.stderr}")
        else:
            print("[SUCCESS] 360p-Konvertierung abgeschlossen!")
            video = Video.objects.get(id=video_id)
            relative_path = target.replace(settings.MEDIA_ROOT + '/', '')
            video.file360p.name = relative_path
            video.save(update_fields=['file360p'])
    except Exception as e:
        print(f"[CRITICAL] 360p-Ausnahme: {str(e)}")


@job('queue_240p')
def convert_240p(video_id, source):
    target = source[:-4] + '_240p.mp4'
    cmd = [
        'ffmpeg',
        '-i', source,
        '-s', '426x240',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]
    try:
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode != 0:
            print(f"[ERROR] 240p-FFmpeg-Fehler:\n{run.stderr}")
        else:
            print("[SUCCESS] 240p-Konvertierung abgeschlossen!")
            video = Video.objects.get(id=video_id)
            relative_path = target.replace(settings.MEDIA_ROOT + '/', '')
            video.file240p.name = relative_path
            video.save(update_fields=['file240p'])
    except Exception as e:
        print(f"[CRITICAL] 240p-Ausnahme: {str(e)}")
