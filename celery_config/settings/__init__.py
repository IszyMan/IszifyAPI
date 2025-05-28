from celery import Celery, shared_task
import celery_config.schedule_config as celeryConfig
import os
from app_config import create_app

app = create_app()


def make_celery(app=app):
    """
    As described in the doc
    """
    celery = Celery(
        app.import_name,
        backend=f"{os.environ.get('REDIS_URL')}",
        broker=f"{os.environ.get('REDIS_URL')}",
    )
    celery.conf.update(app.config)
    celery.config_from_object(celeryConfig)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery()
