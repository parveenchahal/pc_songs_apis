from common import Controller
from logging import Logger
from common import http_responses
from item_model import ItemModel
from songs_library import SongsLibrary
from collections import deque

class SubItemsController(Controller):

    _songs_library: SongsLibrary

    def __init__(self, logger: Logger, songs_library :SongsLibrary):
        super().__init__(logger)
        self._songs_library = songs_library

    def get(self, id, subitem_type: str):
        subitem_type = subitem_type.lower()
        if subitem_type not in ('subfolders', 'files'):
            return http_responses.NotFoundResponse()
        res = []
        q = deque()
        items = self._songs_library.get(id)
        for x in items:
            if x.type == 'folder':
                q.append(x.id)
            if subitem_type == 'subfolders' and x.type == 'folder':
                res.append(x)
            elif subitem_type == 'files' and x.type == 'file':
                res.append(x)

        while len(q):
            id = q.popleft()
            items = self._songs_library.get(id)
            for x in items:
                if x.type == 'folder':
                    q.append(x.id)
                if subitem_type == 'subfolders' and x.type == 'folder':
                    res.append(x)
                elif subitem_type == 'files' and x.type == 'file':
                    res.append(x)
        if subitem_type == 'files':
            res = sorted(res, key=lambda x: x.name)
        return http_responses.JSONResponse(res)