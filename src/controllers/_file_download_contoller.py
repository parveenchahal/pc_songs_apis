from logging import Logger
from common import Controller
from common import http_responses
from songs_library import SongsLibrary

class FileDownloadController(Controller):

    _songs_library: SongsLibrary

    def __init__(self, logger: Logger, songs_library: SongsLibrary):
        super().__init__(logger)
        self._songs_library = songs_library

    def get(self, id):
        content = self._songs_library.download_file(id)
        return http_responses.Response(content, 200, None, 'audio/mpeg')
