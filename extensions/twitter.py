from django.conf import settings

from json import loads as json_loads, dumps as json_dumps

from tweepy import OAuthHandler, API, Client, Stream

auth = OAuthHandler(consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET)
auth.set_access_token(key=settings.ACCESS_TOKEN, secret=settings.ACCESS_TOKEN_SECRET)

APIv1 = API(auth=auth, wait_on_rate_limit=True)
APIv2 = Client(bearer_token=settings.BEARER_TOKEN)


class TwitterStreamer(Stream):
    def __init__(self):
        super().__init__(
            consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET,
            access_token=settings.ACCESS_TOKEN, access_token_secret=settings.ACCESS_TOKEN_SECRET,
        )

    def start_streaming(self):
        from twitter.models import TargetUser
        target_users = list(TargetUser.objects.twitter_user_ids())
        self.filter(follow=target_users)

    def on_connect(self):
        print('Streamer started')

    def on_data(self, data):
        dict_tweet = json_loads(data)
        json_tweet = json_dumps(dict_tweet)
        print(f'{json_tweet}')

    def on_error(self, status):
        print(status)


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
