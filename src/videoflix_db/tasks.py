import subprocess
from django_rq import job


@job('queue_720p')
def convert_720p(source):
    target = source[:-4] + '_720p.mp4'
    cmd = 'ffmpeg -i "{}" -s 1280x720 -c:v libx264 -crf 23 -c:a aac -strict -2 {}' .format(source, target)
    run = subprocess.run(cmd, capture_output=True)
    if run.returncode != 0:
        print(f"720p Fehler: {run.stderr.decode()}")

@job('queue_360p')
def convert_360p(source):
    target = source[:-4] + '_360p.mp4'
    cmd = 'ffmpeg -i "{}" -s 640x360 -c:v libx264 -crf 23 -c:a aac -strict -2 {}' .format(source, target)
    run = subprocess.run(cmd, capture_output=True)
    if run.returncode != 0:
        print(f"720p Fehler: {run.stderr.decode()}")

@job('queue_240p')
def convert_240p(source):
    target = source[:-4] + '_240p.mp4'
    cmd = 'ffmpeg -i "{}" -s 426x240 -c:v libx264 -crf 23 -c:a aac -strict -2 {}' .format(source, target)
    run = subprocess.run(cmd, capture_output=True)
    if run.returncode != 0:
        print(f"720p Fehler: {run.stderr.decode()}")
