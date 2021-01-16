from common import Model
from dataclasses import dataclass

@dataclass
class ItemModel(Model):
    name: str
    type: str
    url: str