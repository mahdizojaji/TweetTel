from django.conf import settings
from django.core.cache import cache
from django.utils.html import escape as html_escape

from celery import shared_task
from celery.result import AsyncResult

from json import loads as json_loads

from logging import getLogger


logger = getLogger(__name__)


def celery_ready_worker(sender=None, headers=None, body=None, **kwargs):
    twitter_streamer.delay()


def task_revoked(sender=None, headers=None, body=None, request=None, **kwargs):
    cache.delete('STREAMER_TASK_ID')
    twitter_streamer.delay()


def task_post_run(sender=None, headers=None, body=None, **kwargs):
    running_task_id = cache.get('STREAMER_TASK_ID')
    if running_task_id == kwargs['task_id']:
        cache.delete('STREAMER_TASK_ID')


def worker_shutting_down(sender=None, headers=None, body=None, **kwargs):
    cache.delete('STREAMER_TASK_ID')


@shared_task(bind=True, ignore_result=True)
def twitter_streamer(self):
    from extensions.twitter.streaming import TwitterStreamer

    running_task_id = cache.get('STREAMER_TASK_ID', '')
    running_task = AsyncResult(running_task_id)
    if running_task_id and running_task.status == 'PENDING':
        logger.error('Task already is running')
        return
    else:
        cache.set('STREAMER_TASK_ID', f'{self.request.id}')

    streamer = TwitterStreamer()
    streamer.idle()


@shared_task(ignore_result=True)
def send_tweet_to_telegram(data):
    from twitter.models import TargetUser

    from extensions.telegram import tg_methods
    from extensions.twitter import generate_tweet_image
    from extensions.twitter.types import Tweet

    tweet: Tweet = Tweet().parse(None, json_loads(data))

    if not TargetUser.objects.filter(twitter_id=tweet.user.id_str).exists():
        return
    if tweet.is_reply:
        return
    if tweet.is_retweet:
        return

    tweet_image = generate_tweet_image(
        name=tweet.user.name,
        username=tweet.user.username,
        text=tweet.text,
        time=tweet.created_at.strftime('%Y-%m-%d'),
        date=tweet.created_at.strftime('%H:%M:%S'),
        device=tweet.source,
        image_url=tweet.user.profile_image_url,
        is_verified=tweet.user.verified,
        images=tweet.media_urls,
    )

    text = f'<b>Type: </b> {tweet.type}\n'
    text += f'👤 <a href="{tweet.user.url}"> {html_escape(tweet.user.name)} </a> '
    text += f'🔗 <a href="{tweet.url}">' + 'توییت' + '</a>\n'
    text += f'#{html_escape(tweet.user.username)}'

    if tweet_image:
        tg_methods.send_photo(
            chat_id=settings.TELEGRAM_CHAT_ID,
            photo=tweet_image,
            caption=text,
            parse_mode='HTML',
        )
    else:
        tg_methods.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode='HTML',
        )
