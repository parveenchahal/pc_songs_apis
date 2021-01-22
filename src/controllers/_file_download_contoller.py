from common import Controller
from logging import Logger
from requests import request
from common import http_responses

class FileDownloadController(Controller):

    _token: str
    _file_content_url: str = 'https://api.box.com/2.0/files/{id}/content'
    
    def __init__(self, logger: Logger, token: str):
        super().__init__(logger)
        self._token = token

    def get(self, id):
        url = self._file_content_url.format_map({'id': id})
        res = request("GET", url, headers={"Authorization": f'Bearer {self._token}'})
        return http_responses.Response(res.content, 200, None, 'audio/mpeg')
