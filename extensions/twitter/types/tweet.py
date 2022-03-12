import datetime

from tweepy.models import Status, Place

from .twitter_user import TwitterUser


class Tweet(Status):
    def __init__(self, api=None):
        super().__init__(api)
        self.json: dict or None = None
        self.created_at: datetime.datetime = None
        self.id: int or None = None
        self.id_str: str or None = None
        self.text: str or None = None
        self.source: str or None = None
        self.source_url: str or None = None
        self.truncated: bool or None = None
        self.in_reply_to_status_id: int or None = None
        self.in_reply_to_status_id_str: str or None = None
        self.in_reply_to_user_id: int or None = None
        self.in_reply_to_user_id_str: str or None = None
        self.in_reply_to_screen_name: str or None = None
        self.user: TwitterUser = None
        self.author: TwitterUser = None
        self.geo: dict or None = None
        self.coordinates: dict or None = None
        self.place: Place = None
        self.contributors: list or None = None
        self.is_quote_status: bool or None = None
        self.quote_count: int or None = None
        self.reply_count: int or None = None
        self.retweet_count: int or None = None
        self.favorite_count: int or None = None
        self.entities: dict or None = None
        self.favorited: bool or None = None
        self.retweeted: bool or None = None
        self.filter_level: str or None = None
        self.lang: str or None = None
        self.timestamp_ms: str or None = None
        self.retweeted_status: Status = None
        self.quoted_status: Status = None
        self.timestamp: str or None = None
        self.is_reply: bool or None = None
        self.reply: dict or None = None
        self.is_retweet: bool or None = None
        self.retweet: Tweet = None
        self.is_quote: bool or None = None
        self.quote: Tweet = None
        self.url: str or None = None
        self.type: str or None = None
        self.media_urls: list = []

    @classmethod
    def parse(cls, api, json) -> 'Tweet':
        status = super().parse(api, json)
        status.json = json
        status.timestamp = json.get('timestamp_ms')
        if json['in_reply_to_status_id'] or json['in_reply_to_user_id']:
            status.is_reply = True
        else:
            status.is_reply = False
        status.reply = {
            'id': json['in_reply_to_status_id'],
            'user_id': json['in_reply_to_user_id'],
            'username': json['in_reply_to_screen_name'],
        }
        status.is_retweet = True if json.get('retweeted_status') else False
        status.retweet = Tweet().parse(api, json['retweeted_status']) if status.is_retweet else None
        if json.get('is_quote_status'):
            status.is_quote = True
        else:
            status.is_quote = False
        status.quote = Tweet().parse(api, json['quoted_status']) if status.is_quote else None
        status.user = TwitterUser().parse(api, json['user'])
        status.author = TwitterUser().parse(api, json['user'])
        if media := json.get('extended_entities', {}).get('media'):
            for media_item in media:
                status.media_urls.append(media_item['media_url_https'])
        if status.is_quote:
            status.url = json['quoted_status_permalink']['expanded']
        else:
            status.url = f'https://twitter.com/{status.user.screen_name}/status/{status.id}'
        if full_text := json.get('extended_tweet', {}).get('full_text'):
            status.text = full_text
        if status.is_retweet:
            status.type = 'retweet'
        elif status.is_quote:
            status.type = 'quote'
        elif status.is_reply:
            status.type = 'reply'
        else:
            status.type = 'tweet'
        return status
