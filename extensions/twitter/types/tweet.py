from .twitter_user import TwitterUser


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
