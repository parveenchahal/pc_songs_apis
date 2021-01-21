from common import Controller
from logging import Logger
from common import http_responses
from songs_library import SongsLibrary


class FolderController(Controller):

    _songs_library: SongsLibrary

    def __init__(self, logger: Logger, songs_library :SongsLibrary):
        super().__init__(logger)
        self._songs_library = songs_library

    def get(self, id):
        res = self._songs_library.get(id)
        return http_responses.JSONResponse(res)
