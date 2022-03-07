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
