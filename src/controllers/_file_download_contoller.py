import io
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
        def stream():
            try:
                bio = io.BytesIO(content)
                while True:
                    chunk = bio.read(1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                bio.close()
        return http_responses.Response(stream(), 200, None, 'audio/mpeg')
