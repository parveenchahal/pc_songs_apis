from datetime import datetime, timedelta
from threading import RLock
from requests import get as http_get, request
import copy
from collections import deque
from common.utils import parse_json
from common import Scheduler
from typing import List, Tuple
from item_model import ItemModel
from utils import parse_folders_and_files_list

class SongsLibrary(object):

    _folder_url: str = 'https://api.box.com/2.0/folders/{id}?limit=1000'
    _cached_folders: dict = {0: []}
    _cached_files: dict = {}
    _cache_timeout: timedelta = timedelta(days=1)
    _lock: RLock
    _token: str
    _audio_file_extensions: Tuple[str] = ('.mp3',)

    def __init__(self, token: str) -> None:
        self._token = token
        self._lock = RLock()
        self._schedular = Scheduler(self._fetch_and_cache, self._cache_timeout, 'song_library_schedular')
        self._schedular.start()
    
    def get_folder(self, folder_id: str = '0') -> List[ItemModel]:
        with self._lock:
            return copy.deepcopy(self._cached_folders.get(folder_id, []))

    def get_file(self, file_id: str = '0') -> List[ItemModel]:
        with self._lock:
            return copy.deepcopy(self._cached_files.get(file_id, None))

    def _fetch_and_cache(self):
        folders_data = {}
        files_data = {}
        q = deque()
        res = self._get_from_box('0')
        folders_data['0'] = res
        for x in res:
            if x.type == 'folder':
                q.append(x.id)
            elif x.type == 'file':
                files_data[x.id] = x
        while len(q) > 0:
            id = q.popleft()
            res = self._get_from_box(id)
            folders_data[id] = res
            for x in res:
                if x.type == 'folder':
                    q.append(x.id)
                elif x.type == 'file':
                    files_data[x.id] = x
        with self._lock:
            self._cached_folders = folders_data
            self._cached_files = files_data
    
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
        return res