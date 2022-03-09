from extensions.http_requests import BasicHttpRequest

from json import dumps as json_dumps

from django.conf import settings

from io import IOBase


class TelegramMethod(BasicHttpRequest):
    def __init__(self, bot_token=settings.TELEGRAM_BOT_TOKEN, base_url="https://api.telegram.org"):
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKE is not set in .env")
        self._base_url = f"{base_url}/bot{bot_token}"

    @property
    def base_url(self):
        return self._base_url

    def _request(self, http_method: str, url: str, data: dict = None, files: dict = None, **kwargs):
        if data:
            kwargs['data'] = self._delete_none_values(data)
        if files:
            kwargs['files'] = self._delete_none_values(files)
        return super(TelegramMethod, self)._request(http_method, url, **kwargs)

    def _make_url(self, endpoint: str):
        return f"{self.base_url}/{endpoint}"

    def _make_request(self, http_method: str, endpoint: str, data: dict = None, files: dict = None):
        if data.get('reply_markup'):
            data['reply_markup'] = json_dumps(data['reply_markup'])

        for field, file in (files or {}).items():
            if isinstance(file.content, str):
                data[field] = file
                del files[field]
            else:
                files[field] = file.prepared_data()

        return self._request(http_method=http_method, url=self._make_url(endpoint), data=data, files=files)

    def get_me(self):
        http_method = 'GET'
        endpoint = "getMe"
        return self._make_request(http_method=http_method, endpoint=endpoint).json()

    def send_message(self, chat_id: str or int, text, parse_mode: str = None, entities: list = None,
                     disable_web_page_preview: bool = None, disable_notification: bool = None,
                     protect_content: bool = None, reply_to_message_id: int = None,
                     allow_sending_without_reply: bool = True, reply_markup: dict = None):
        http_method = 'POST'
        endpoint = "sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'entities': entities,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification,
            'protect_content': protect_content,
            'reply_to_message_id': reply_to_message_id,
            'allow_sending_without_reply': allow_sending_without_reply,
            'reply_markup': reply_markup
        }
        return self._make_request(http_method=http_method, endpoint=endpoint, data=data)

    def send_photo(self, chat_id: str or int, photo: str or bytes or IOBase, caption: str = None,
                   parse_mode: str = None, caption_entities: list = None, disable_notification: bool = None,
                   protect_content: bool = None, reply_to_message_id: int = None,
                   allow_sending_without_reply: bool = True, reply_markup: dict = None):
        http_method = 'POST'
        endpoint = "sendPhoto"
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': parse_mode,
            'caption_entities': caption_entities,
            'disable_notification': disable_notification,
            'protect_content': protect_content,
            'reply_to_message_id': reply_to_message_id,
            'allow_sending_without_reply': allow_sending_without_reply,
            'reply_markup': reply_markup,
        }
        files = {
            'photo': self.File(photo, 'photo', 'image/jpeg'),
        }
        return self._make_request(http_method=http_method, endpoint=endpoint, data=data, files=files)
