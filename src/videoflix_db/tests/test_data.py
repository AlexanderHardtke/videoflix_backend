from videoflix_db.models import Video, WatchedVideo

def create_videos(user):
    video = Video.objects.create(name='testvideo', type='nature',image='',file1080p='', uploaded_by=user)