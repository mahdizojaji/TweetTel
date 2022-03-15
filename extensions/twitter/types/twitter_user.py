import datetime

from tweepy.models import User


class TwitterUser(User):
    def __init__(self, api=None):
        super().__init__(api)
        self.json: dict or None = None
        self.id: int or None = None
        self.id_str: str or None = None
        self.name: str or None = None
        self.screen_name: str or None = None
        self.location: str or None = None
        self.url: str or None = None
        self.description: str or None = None
        self.translator_type: str or None = None
        self.protected: bool or None = None
        self.verified: bool or None = None
        self.followers_count: int or None = None
        self.friends_count: int or None = None
        self.listed_count: int or None = None
        self.favourites_count: int or None = None
        self.statuses_count: int or None = None
        self.created_at: str or None = None
        self.utc_offset: int or None = None
        self.time_zone: str or None = None
        self.geo_enabled: bool or None = None
        self.lang: str or None = None
        self.contributors_enabled: bool or None = None
        self.is_translator: bool or None = None
        self.profile_background_color: str or None = None
        self.profile_background_image_url: str or None = None
        self.profile_background_image_url_https: str or None = None
        self.profile_background_tile: bool or None = None
        self.profile_link_color: str or None = None
        self.profile_sidebar_border_color: str or None = None
        self.profile_sidebar_fill_color: str or None = None
        self.profile_text_color: str or None = None
        self.profile_use_background_image: bool or None = None
        self.profile_image_url: str or None = None
        self.profile_image_url_https: str or None = None
        self.profile_banner_url: str or None = None
        self.default_profile: bool or None = None
        self.default_profile_image: bool or None = None
        self.following: bool or None = None
        self.follow_request_sent: bool or None = None
        self.notifications: bool or None = None
        self.withheld_in_countries: list or None = None
        self.created_at: datetime.datetime = None
        self.username: str or None = None
        self.url: str or None = None
        self.image_data: dict or None = None

    @classmethod
    def parse(cls, api, json) -> 'TwitterUser':
        user = super().parse(api, json)
        user.json = json
        user.username = json['screen_name']
        user.url = f'https://twitter.com/{user.username}/'
        user.image_data = {
            'profile_image_url': json.get('profile_image_url'),
            'profile_image_url_https': json.get('profile_image_url_https'),
            'profile_banner_url': json.get('profile_banner_url')
        }
        return user
