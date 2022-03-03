from django.conf import settings

from twitter.tasks import send_tweet_to_telegram

from json import loads as json_loads, dumps as json_dumps

from tweepy import OAuthHandler, API, Client, Stream

from logging import getLogger

auth = OAuthHandler(consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET)
auth.set_access_token(key=settings.ACCESS_TOKEN, secret=settings.ACCESS_TOKEN_SECRET)

APIv1 = API(auth=auth, wait_on_rate_limit=True)
APIv2 = Client(bearer_token=settings.BEARER_TOKEN)

logger = getLogger(__name__)


class TwitterUser:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.id = raw_data['id']
        self.name = raw_data['name']
        self.screen_name = raw_data['screen_name']
        self.created_at = raw_data['created_at']
        self.url = f'https://twitter.com/{self.screen_name}/'
        self.image_data = {
            'profile_image_url': raw_data['profile_image_url'],
            'profile_image_url_https': raw_data['profile_image_url_https'],
            'profile_banner_url': raw_data['profile_banner_url']
        }


class Tweet:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.id = raw_data['id']
        self.text = raw_data['text']
        self.timestamp = raw_data.get('timestamp_ms')
        if raw_data['in_reply_to_status_id'] or raw_data['in_reply_to_user_id']:
            self.is_reply = True
        else:
            self.is_reply = False
        self.reply = {
            'in_reply_to_status_id': raw_data['in_reply_to_status_id'],
            'in_reply_to_user_id': raw_data['in_reply_to_user_id'],
            'in_reply_to_screen_name': raw_data['in_reply_to_screen_name'],
        }
        self.is_retweet = True if raw_data.get('retweeted_status') else False
        self.retweet = Tweet(raw_data=raw_data['retweeted_status']) if self.is_retweet else None
        if raw_data.get('is_quote_status'):
            self.is_quote = True
        else:
            self.is_quote = False
        self.quote = Tweet(raw_data=raw_data['quoted_status']) if self.is_quote else None
        self.user = TwitterUser(raw_data=raw_data['user'])
        if self.is_quote:
            self.url = raw_data['quoted_status_permalink']['expanded']
        else:
            self.url = f'https://twitter.com/{self.user.screen_name}/status/{self.id}'
        if self.is_retweet:
            self.type_ = 'retweet'
        elif self.is_quote:
            self.type_ = 'quote'
        elif self.is_reply:
            self.type_ = 'reply'
        else:
            self.type_ = 'tweet'


class TwitterStreamer(Stream):
    def __init__(self):
        super().__init__(
            consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET,
            access_token=settings.ACCESS_TOKEN, access_token_secret=settings.ACCESS_TOKEN_SECRET,
        )

    def start_streaming(self):
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

    def on_status(self, status):
        send_tweet_to_telegram.delay(json_dumps(status._json))

    def on_error(self, status):
        logger.error(f'{status}')


def get_user_info(data):
    """
    Get user data from Twitter API
    :param data: Twitter user id or username
    """
    if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
        response = APIv2.get_user(id=str(data))
    elif isinstance(data, str):
        response = APIv2.get_user(username=data)
    else:
        raise ValueError('Data must be twitter user id username')

    if response.errors:
        raise Exception(response.errors)
    return response
