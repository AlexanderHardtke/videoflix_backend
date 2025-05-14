from videoflix_db.models import Video, WatchedVideo, UserProfil

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
    
def create_videos(user):
    return Video.objects.create(
        name='exampleName', type='animals', image='src/media/images/Alex.PNG',
        file1080p='src/media/movies/220kg_Deadlift.mp4', uploaded_by=user)
