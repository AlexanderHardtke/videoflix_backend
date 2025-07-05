from videoflix_db.models import Video, UserProfil
from django.core.files.uploadedfile import SimpleUploadedFile


invalid_video_pk = 254


def create_admin():
    return UserProfil.objects.create_superuser(
        email='staff@mail.de',
        username='staff@mail.de',
        password='staffpw',
    )


def create_user():
    user = UserProfil.objects.create_user(
        email='example@mail.de',
        username='example@mail.de',
        password='examplePassword',
    )
    user.is_active = True
    user.is_verified = True
    user.save()
    return user


def create_other_user():
    user = UserProfil.objects.create_user(
        email='other@mail.de',
        username='other@mail.de',
        password='otherPassword',
    )
    user.is_active = True
    user.is_verified = True
    user.save()
    return user


def create_incative_user():
    user = UserProfil.objects.create_user(
        email='inactiveuser@mail.de',
        username='inactiveuser@mail.de',
        password='examplePassword'
    )
    user.is_active = False
    user.is_verified = False
    user.save()
    return user


def create_video(user):
    return Video.objects.create(
        name='exampleName',
        video_type='training',
        image=SimpleUploadedFile(
            "test.jpg", b"fake image content", content_type="image/jpeg"),
        file1080p=SimpleUploadedFile(
            "test.mp4", b"fake video content", content_type="video/mp4"),
    )
