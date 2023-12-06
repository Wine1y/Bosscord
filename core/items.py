from json import load
from enum import Enum
from dataclasses import dataclass, fields
from abc import ABC
from typing import Optional, Dict, Any, List

from core.settings import settings


class ItemsError(Exception):
    ...

class ItemType(Enum):
    SKILL = "skills"
    PET = "pets"
    ARMOR = "armors"
    WEAPON = "weapons"

class ActiveEffectType(Enum):
    HEAL = "heal"
    DAMAGE = "damage"
    DISABLE_PET = "disable_pet"
    DISABLE_SKILL = "disable_skill"
    DISARM = "disarm"

ACTIVE_ITEM_TYPES = ["skills", "pets"]

@dataclass
class PassiveItemEffect(ABC):
    attack_boost: Optional[int]
    armor_boost: Optional[float]
    health_boost: Optional[int]
    crit_chance_boost: Optional[float]
    crit_damage_boost: Optional[float]

@dataclass
class Effect():
    type: ActiveEffectType
    amount: Optional[int]

@dataclass
class ActiveItemEffect(ABC):
    interception_rate: float
    effects: List[Effect]
    max_uses_per_battle: Optional[int]

@dataclass
class Item:
    id: str
    name: str
    price: int
    required_level: Optional[int]
    type: ItemType
    passive_effect: Optional[PassiveItemEffect]
    active_effect: Optional[ActiveItemEffect]
    image: Optional[str]

    @classmethod
    def load_active_item(cls, json_data: Dict[str, Any], item_type: ItemType) -> "Item":
        try:
            return cls(
                json_data["id"],
                json_data["name"],
                json_data["price"],
                json_data.get("required_level"),
                item_type,
                None,
                ActiveItemEffect(
                    json_data["interception_rate"],
                    [Effect(ActiveEffectType(effect_data["name"]), effect_data.get("amount")) for effect_data in json_data["active_effects"]],
                    json_data.get("max_uses_per_battle")
                ),
                json_data.get("image")
            )
        except Exception:
            raise ItemsError(f"Item {json_data.get('name')} with id {json_data.get('id')} is invalid")

    @classmethod
    def load_passive_item(cls, json_data: Dict[str, Any], item_type: ItemType) -> "Item":
        try:
            return cls(
                json_data["id"],
                json_data["name"],
                json_data["price"],
                json_data.get("required_level"),
                item_type,
                PassiveItemEffect(
                    *[json_data.get(field.name) for field in fields(PassiveItemEffect)]
                ),
                None,
                json_data.get("image")
            )
        except Exception:
            raise ItemsError(f"Item {json_data.get('name')} with id {json_data.get('id')} is invalid")

class Items():
    all_items: List[Item] = list()

    def __init__(self, items_path: str) -> None:
        try:
            with open(items_path, "r", encoding="utf-8") as json_items:
                for key, value in load(json_items).items():
                    type = ItemType(key)
                    for item_json in value:
                        if key in ACTIVE_ITEM_TYPES:
                            self.all_items.append(Item.load_active_item(item_json, type))
                        else:
                            self.all_items.append(Item.load_passive_item(item_json, type))
        except Exception:
            raise ItemsError(f"Items file at {items_path} is invalid or not found")
        else:
            self.check_duplicates()
    
    def check_duplicates(self) -> None:
        ids = {}
        for item in self.all_items:
            if ids.get(item.id) is not None:
                raise ItemsError(f"Two or more items have the same ID: {item.id}")
            else:
                ids[item.id] = True
    @property
    def skills(self) -> List[Item]:
        skill_type = ItemType.SKILL
        return [item for item in self.all_items if item.type == skill_type]
    
    @property
    def pets(self) -> List[Item]:
        pet_type = ItemType.PET
        return [item for item in self.all_items if item.type == pet_type]
    
    @property
    def armors(self) -> List[Item]:
        armor_type = ItemType.ARMOR
        return [item for item in self.all_items if item.type == armor_type]
    
    @property
    def weapons(self) -> List[Item]:
        weapon_type = ItemType.WEAPON
        return [item for item in self.all_items if item.type == weapon_type]
    
    def item_by_id(self, id: str) -> Item:
        for item in self.all_items:
            if item.id == id:
                return item

    def items_by_ids(self, ids: List[str]) -> List[Item]:
        return [item for item in self.all_items if item.id in ids]

items = Items(settings.get_config("ITEMS_PATH"))