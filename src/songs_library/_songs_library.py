from datetime import timedelta
from logging import Logger
from requests import request
import json
from collections import deque
from common.utils import bytes_to_string, decode_base64, parse_json, encode_base64, string_to_bytes
from common import Scheduler
from common.exceptions import KeyNotFoundInCacheError
from common.cache import Cache, cached
from typing import List, Tuple, Union
from item_model import ItemModel
from utils import parse_folders_and_files_list

class SongsLibrary(object):

    _folder_url: str = 'https://api.box.com/2.0/folders/{id}?limit=1000'
    _file_content_url: str = 'https://api.box.com/2.0/files/{id}/content'
    _token: str
    _audio_file_extensions: Tuple[str] = ('.mp3',)
    _refresh_interval: timedelta = timedelta(days=1)
    _cache: Cache

    def __init__(self, logger: Logger, token: str, cache: Cache) -> None:
        self._logger = logger
        self._token = token
        self._cache = cache
        self._schedular = Scheduler(self._fetch_and_cache, self._refresh_interval, 'song_library_schedular')
        self._schedular.start()
    
    def get(self, item_id: str = '0') -> Union[ItemModel, List[ItemModel]]:
        try:
            return self._cache.get(item_id, self._deserialize)
        except KeyNotFoundInCacheError:
            return []

    def download_file(self, file_id):
        @cached(
            self._cache,
            ttl=timedelta(hours=1),
            serializer=lambda x: bytes_to_string(encode_base64(x)),
            deserializer=lambda x: decode_base64(string_to_bytes(x)))
        def wrapper(file_id, dummy):
            url = self._file_content_url.format_map({'id': file_id})
            res = request("GET", url, headers={"Authorization": f'Bearer {self._token}'})
            return res.content
        return wrapper(file_id, 'dummy')

    def force_update(self):
        self._fetch_and_cache()

    def _serialize(self, data: Union[ItemModel, List[ItemModel]]) -> str:
        if type(data) == list:
            data = [ItemModel.to_dict(x) for x in data]
        else:
            data = ItemModel.to_dict(data)
        return json.dumps(data)

    def _deserialize(self, data: str) -> Union[ItemModel, List[ItemModel]]:
        data = json.loads(data)
        if type(data) == list:
            data = [ItemModel.from_dict(ItemModel, x) for x in data]
        else:
            data = ItemModel.from_dict(ItemModel, data)
        return data

    def _fetch_and_cache(self):
        self._logger.info('Refresh songs library started.')
        q = deque()
        res = self._get_from_box('0')
        self._cache.set('0', res, serializer=self._serialize)
        for item in res:
            if item.type == 'folder':
                q.append(item.id)
            elif item.type == 'file':
                self._cache.set(item.id, item, serializer=self._serialize)
        while len(q) > 0:
            id = q.popleft()
            res = self._get_from_box(id)
            self._cache.set(id, res, serializer=self._serialize)
            for item in res:
                if item.type == 'folder':
                    q.append(item.id)
                elif item.type == 'file':
                    self._cache.set(item.id, item, serializer=self._serialize)
        self._logger.info('Refresh songs library completed.')

    def _remove_file_extension(self, li: List[ItemModel]):
        for x in li:
            if x.type == 'file':
                x.name = x.name[0:x.name.rfind('.')]
    
    def _filter(self, li: List[ItemModel]):
        def wrapper(x: ItemModel):
            if x.type == 'file':
                return x.name.lower().endswith(self._audio_file_extensions)
            return True
        return list(filter(wrapper, li))

    def _get_from_box(self, id) -> List[ItemModel]:
        url = self._folder_url.format_map({'id': id})
        res = request("GET", url, headers={"Authorization": f'Bearer {self._token}'})
        res = parse_json(res.text)
        res = res['item_collection']['entries']
        res = parse_folders_and_files_list(res)
        res = self._filter(res)
        self._remove_file_extension(res)
        return res