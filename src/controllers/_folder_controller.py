from common import Controller
from logging import Logger
from requests import request
from common.utils import parse_json
from common import http_responses
from utils import parse_folders_and_files_list

class FolderController(Controller):

    _token: str
    _folder_url: str = 'https://api.box.com/2.0/folders/{id}'
    
    def __init__(self, logger: Logger, token: str):
        super().__init__(logger)
        self._token = token

    def get(self, id):
        url = self._folder_url.format_map({'id': id})
        res = request("GET", url, headers={"Authorization": f'Bearer {self._token}'})
        res = parse_json(res.text)
        res = res['item_collection']['entries']
        res = parse_folders_and_files_list(res)
        return http_responses.JSONResponse(res)
