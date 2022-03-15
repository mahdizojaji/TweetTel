from django.conf import settings

from logging import getLogger
from tweepy.streaming import Stream
from tweepy.models import Status
from json import dumps as json_dumps

from twitter.tasks import send_tweet_to_telegram


logger = getLogger(__name__)


class TwitterStreamer(Stream):
    def __init__(self):
        super().__init__(
            consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET,
            access_token=settings.ACCESS_TOKEN, access_token_secret=settings.ACCESS_TOKEN_SECRET,
        )

    def idle(self):
        from twitter.models import TargetUser
        target_users = list(TargetUser.objects.twitter_user_ids())
        if not target_users:
            logger.warning('No target users found. Streaming not started. '
                           'Please add target users and use update streamer target users action.')
            return
        self.filter(follow=target_users)

    def on_connect(self):
        logger.info('Streamer started')

    def on_disconnect(self):
        logger.info('Streamer stopped')

    def on_status(self, status: Status):
        send_tweet_to_telegram.delay(json_dumps(status._json))

    def on_error(self, status):
        logger.error(f'{status}')
