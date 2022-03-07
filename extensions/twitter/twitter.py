from django.conf import settings

from tweepy import OAuthHandler, API, Client

from logging import getLogger


auth = OAuthHandler(consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET)
auth.set_access_token(key=settings.ACCESS_TOKEN, secret=settings.ACCESS_TOKEN_SECRET)

APIv1 = API(auth=auth, wait_on_rate_limit=True)
APIv2 = Client(bearer_token=settings.BEARER_TOKEN)

logger = getLogger(__name__)


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
