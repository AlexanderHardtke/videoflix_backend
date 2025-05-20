from django.apps import AppConfig


class VideoflixDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoflix_db'

    def ready(self):
        from . import signals
