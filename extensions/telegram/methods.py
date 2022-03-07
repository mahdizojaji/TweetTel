from requests import sessions
from requests.adapters import HTTPAdapter

from django.conf import settings


class TelegramMethod:
    def __init__(self, bot_token=settings.TELEGRAM_BOT_TOKEN, base_url="https://api.telegram.org"):
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKE is not set in .env")
        self._base_url = f"{base_url}/bot{bot_token}"
        self.session = sessions.Session()
        self.session.mount(base_url, HTTPAdapter(max_retries=3))

    def _make_url(self, endpoint):
        return f"{self._base_url}/{endpoint}"

    def _request(self, http_method, endpoint, data=None):
        url = self._make_url(endpoint)
        data = self._clear_none_values(data or {})
        return self.session.request(method=http_method, url=url, data=data)

    @staticmethod
    def _clear_none_values(data):
        return {k: v for k, v in data.items() if v is not None}

    def get_me(self):
        http_method = 'GET'
        endpoint = "getMe"
        return self._request(http_method, endpoint).json()

    def send_message(self, chat_id, text, parse_mode=None, entities=None, disable_web_page_preview=None,
                     disable_notification=None, protect_content=None, reply_to_message_id=None,
                     allow_sending_without_reply=True, reply_markup=None):
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
            'reply_markup': reply_markup,
        }
        return self._request(http_method, endpoint, data).json()
