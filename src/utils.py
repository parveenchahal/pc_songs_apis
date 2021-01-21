import config
from common import Model
from typing import List
from item_model import ItemModel

def parse_folders_and_files_list(items: list) -> List[ItemModel]:
    def parse_item(item):
        if str.lower(item['type']) == 'folder':
            url = config.FolderUrlTemplate.format_map({'id': item['id']})
            return ItemModel(item['id'], item['name'], item['type'], url)
        elif str.lower(item['type']) == 'file':
            url = config.FileContentUrlTemplate.format_map({'id': item['id']})
            return ItemModel(item['id'], item['name'], item['type'], url)
    return [parse_item(x) for x in items]