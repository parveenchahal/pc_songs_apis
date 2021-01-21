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
    _cached_data: dict = {0: []}
    _cache_timeout: timedelta = timedelta(days=1)
    _lock: RLock
    _token: str
    _audio_file_extensions: Tuple[str] = ('.mp3',)

    def __init__(self, token: str) -> None:
        self._token = token
        self._lock = RLock()
        self._schedular = Scheduler(self._fetch_and_cache, self._cache_timeout, 'song_library_schedular')
        self._schedular.start()
    
    def get(self, folder_id: str = '0') -> List[ItemModel]:
        with self._lock:
            return copy.deepcopy(self._cached_data.get(folder_id, []))

    def _fetch_and_cache(self):
        data = {}
        q = deque()
        res = self._get_from_box('0')
        data['0'] = res
        for x in res:
            if x.type == 'folder':
                q.append(x.id)
        while len(q) > 0:
            id = q.popleft()
            res = self._get_from_box(id)
            data[id] = res
            for x in res:
                if x.type == 'folder':
                    q.append(x.id)
        with self._lock:
            self._cached_data = data
    
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