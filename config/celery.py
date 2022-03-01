from __future__ import absolute_import

import os

from django.conf import settings
from celery import Celery, signals

from twitter.tasks import (
    celery_ready_worker, task_post_run, worker_shutting_down, task_revoked,
    twitter_streamer,
)


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

signals.worker_ready.connect(celery_ready_worker)
signals.task_postrun.connect(task_post_run, sender=twitter_streamer)
signals.task_revoked.connect(task_revoked, sender=twitter_streamer)
signals.worker_shutting_down.connect(worker_shutting_down)
