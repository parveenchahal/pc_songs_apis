from datetime import timedelta
import os
from flask import Flask
from flask_restful import Api
from redis import Redis
from common import AADToken
from common.cache.redis import RedisCache
from common.key_vault import KeyVaultSecret
import config
import logging
from controllers import FolderController, FileDownloadController, SubItemsController, FileController, ForceUpdateController
from songs_library import SongsLibrary

app = Flask(__name__)
api = Api(app)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)

redis_client = Redis(host='redis-service.default')

#============================== AAD Token ==========================================
AAD_IDENTITY_TENANT = os.environ['AAD_IDENTITY_TENANT']
AAD_IDENTITY_CLIENTID = os.environ['AAD_IDENTITY_CLIENTID']
AAD_IDENTITY_SECRET = os.environ['AAD_IDENTITY_SECRET']
key_vault_token = AADToken(AAD_IDENTITY_CLIENTID, AAD_IDENTITY_SECRET, 'https://vault.azure.net', tenant=AAD_IDENTITY_TENANT)
#===================================================================================

box_auth_secret = KeyVaultSecret(config.KeyVaultName, config.BoxAuthSecretName, key_vault_token).get()

songs_library = SongsLibrary(logger, box_auth_secret, RedisCache(redis_client, timedelta(days=30), 'pcsongs'))

api.add_resource(FolderController, '/pc_songs/folders/<id>', endpoint="folders", resource_class_args=(logger, songs_library))
api.add_resource(FileController, '/pc_songs/files/<id>', endpoint="files", resource_class_args=(logger, songs_library))
api.add_resource(SubItemsController, '/pc_songs/folders/<id>/<subitem_type>', endpoint="folder_subfolders", resource_class_args=(logger, songs_library))
api.add_resource(FileDownloadController, '/pc_songs/files/<id>/content', endpoint="file_content", resource_class_args=(logger, songs_library))
api.add_resource(ForceUpdateController, '/pc_songs/forceupdate', endpoint="force_update", resource_class_args=(logger, songs_library))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)