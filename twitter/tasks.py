from django.core.cache import cache

from celery import shared_task
from celery.result import AsyncResult


def celery_ready_worker(sender=None, headers=None, body=None, **kwargs):
    twitter_streamer.delay()


def task_post_run(sender=None, headers=None, body=None, **kwargs):
    running_task_id = cache.get('STREAMER_TASK_ID')
    if running_task_id == kwargs['task_id']:
        cache.delete('STREAMER_TASK_ID')


def worker_shutting_down(sender=None, headers=None, body=None, **kwargs):
    cache.delete('STREAMER_TASK_ID')


@shared_task(bind=True, ignore_result=True)
def twitter_streamer(self):
    from extensions import twitter
    running_task_id = cache.get('STREAMER_TASK_ID', '')
    running_task = AsyncResult(running_task_id)
    if running_task_id and running_task.status == 'PENDING':
        print('Task already is running')
        return
    else:
        cache.set('STREAMER_TASK_ID', f'{self.request.id}')

    streamer = twitter.TwitterStreamer()
    streamer.start_streaming()
