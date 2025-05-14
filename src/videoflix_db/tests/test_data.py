from videoflix_db.models import Video, WatchedVideo, UserProfil
from django.core.files.uploadedfile import SimpleUploadedFile


invalid_video_pk = 254


def create_admin():
    return UserProfil.objects.create_superuser(
        email='staff@mail.de', username='staff@mail.de',
        password='staffpw', is_staff=True, email_confirmed=True)


def create_user():
    return UserProfil.objects.create_user(
        email='example@mail.de', username='example@mail.de',
        password='examplePassword', email_confirmed=True)


def create_incative_user():
    return UserProfil.objects.create_user(
        email='inactiveuser@mail.de', username='inactiveuser@mail.de',
        password='examplePassword', email_confirmed=False)


def create_video(user):
    return Video.objects.create(
        name='exampleName',
        type='training',
        image=SimpleUploadedFile(
            "test.jpg", b"fake image content", content_type="image/jpeg"),
        file1080p=SimpleUploadedFile(
            "test.mp4", b"fake video content", content_type="video/mp4"),
        uploaded_by=user
    )
