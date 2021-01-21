from common import Model
from dataclasses import dataclass

@dataclass
class ItemModel(Model):
    id: str
    name: str
    type: str
    url: str