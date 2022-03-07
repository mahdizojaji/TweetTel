from django.conf import settings
from django.core.cache import cache
from django.utils.html import escape

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
    from extensions.telegram import tg_methods
    from extensions.twitter.types import Tweet

    data = json_loads(data)
    tweet = Tweet().parse(None, data)

    if tweet.is_reply:
        return
    elif tweet.is_retweet:
        text = f"""
<a href="{tweet.url}"> 📩 Tweet Data: </a>
\t<b>Type:</b> {tweet.type}
\t<b>ID:</b> {tweet.id}

<a href="{tweet.retweet.url}"> 🔗 Retweet Data: </a>
\t<b>Type:</b> {tweet.retweet.type}
\t<b>ID:</b> {tweet.retweet.id}

<a href="{tweet.user.url}"> 👤 User Data: </a>
\t<b>ID:</b> {tweet.user.id}
\t<b>Name:</b> {escape(tweet.user.name)}
\t<b>Username:</b> {escape(tweet.user.screen_name)}

📍 #{escape(tweet.user.screen_name)}
            """
    elif tweet.is_quote:
        text = f"""
<a href="{tweet.url}"> 📩 Tweet Data: </a>
\t<b>Type:</b> {tweet.type}
\t<b>ID:</b> {tweet.id}

<a href="{tweet.quote.url}"> 💬 Quote Data: </a>
\t<b>Type:</b> {tweet.quote.type_}
\t<b>ID:</b> {tweet.quote.id}

<a href="{tweet.user.url}"> 👤 User Data: </a>
\t<b>ID:</b> {tweet.user.id}
\t<b>Name:</b> {escape(tweet.user.name)}
\t<b>Username:</b> {escape(tweet.user.screen_name)}

📍 #{escape(tweet.user.screen_name)}
"""
    else:
        text = f"""
<a href="{tweet.url}"> 📩 Tweet Data: </a>
\t<b>Type:</b> {tweet.type}
\t<b>ID:</b> {tweet.id}

<a href="{tweet.user.url}"> 👤 User Data: </a>
\t<b>ID:</b> {tweet.user.id}
\t<b>Name:</b> {escape(tweet.user.name)}
\t<b>Username:</b> {escape(tweet.user.screen_name)}

📍 #{escape(tweet.user.screen_name)}
    """
    logger.info(tg_methods.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text=text,
        parse_mode='HTML',
    ))
