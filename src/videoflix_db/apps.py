from django.apps import AppConfig
from django_rq import get_scheduler
from django.utils import timezone
from tasks import clear_token


class VideoflixDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoflix_db'

    def ready(self):
        from . import signals
        scheduler = get_scheduler('queue_token')

        if not any(job.func_name == 'tasks.clear_token' for job in scheduler.get_jobs()):
            scheduler.schedule(
                scheduled_time=timezone.now(),
                func=clear_token,
                interval=12 * 60 * 60,
                repeat=None,
                queue_name='queue_token'
            )
