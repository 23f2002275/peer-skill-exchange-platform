from celery import Celery
from app import create_app

flask_app = create_app()

celery = Celery(
    flask_app.import_name,
    broker=flask_app.config['CELERY_BROKER_URL'],
    backend=flask_app.config['CELERY_RESULT_BACKEND']
)

celery.conf.update(
    broker_connection_retry_on_startup=True,
    timezone='Asia/Kolkata',
    beat_schedule={
        'close-stale-session-requests': {
            'task': 'tasks.close_stale_requests',
            'schedule': 3600.0
        }
    }
)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

import tasks
