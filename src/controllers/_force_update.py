from common import Controller
from logging import Logger
from common import http_responses
from songs_library import SongsLibrary


class ForceUpdateController(Controller):

    _songs_library: SongsLibrary

    def __init__(self, logger: Logger, songs_library :SongsLibrary):
        super().__init__(logger)
        self._songs_library = songs_library

    def get(self):
        self._songs_library.force_update()
        return http_responses.Response("Done", 200, None, 'text/plain')
