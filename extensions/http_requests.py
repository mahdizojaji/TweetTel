from abc import ABC, abstractmethod

from io import BytesIO, BufferedReader
from json.decoder import JSONDecodeError

from requests.adapters import HTTPAdapter
from requests import Session as requests_Session


class BasicHttpRequest(ABC):
    @property
    @abstractmethod
    def base_url(self):
        raise NotImplementedError

    @abstractmethod
    def _request(self, http_method: str, url: str, **kwargs):
        with requests_Session() as session:
            session.mount(self.base_url, HTTPAdapter(max_retries=3))
            with session.request(method=http_method.upper(), url=url, **kwargs) as response:
                try:
                    return response, response.content, response.json()
                except JSONDecodeError:
                    return response, response.content, {}

    @staticmethod
    def _delete_none_values(payload):
        return {k: v for k, v in payload.items() if v is not None}

    class File:
        def __init__(self, file, file_name=None, mime_type=None):
            self.content = file
            self.file_name = file_name or 'unknown-document'
            self.mime_type = mime_type

        def _file_bytes(self):
            if isinstance(self.content, bytes):
                return self.content
            elif isinstance(self.content, BytesIO):
                return self.content.getvalue()
            elif isinstance(self.content, BufferedReader):
                self.content.seek(0)
                return self.content.read()
            else:
                raise TypeError('File must be bytes, BytesIO or BufferedReader')

        def prepared_data(self):
            if self.mime_type:
                return self.file_name, self._file_bytes(), self.mime_type
            else:
                return self.file_name, self._file_bytes()
