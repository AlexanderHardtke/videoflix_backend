from videoflix_db.models import Video, WatchedVideo, UserProfil


def create_admin():
    UserProfil.objects.create_superuser(
        email='staff@mail.de', username='staff@mail.de',
        password='staffpw', is_staff=True, email_confirmed=True)

def create_user():
    UserProfil.objects.create_user(
        email='example@mail.de', username='example@mail.de',
        password='examplePassword', email_confirmed=True)

def create_incative_user():
    UserProfil.objects.create_user(
        email='inactiveuser@mail.de', username='inactiveuser@mail.de',
        password='examplePassword', email_confirmed=False)
    
def create_videos(user):
    video = Video.objects.create(
        name='testvideo', type='nature', image='',
        file1080p='', uploaded_by=user)
