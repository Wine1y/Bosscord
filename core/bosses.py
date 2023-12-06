from json import load
from dataclasses import dataclass, fields
from typing import List, Optional, Dict

from core.settings import settings
from core.items import items
from logic.profiles_logic import ProfileCalculator


@dataclass
class Boss():
    boss_id: str
    name: str
    hp: int
    attack: int
    armor: float
    crit_chance: float
    crit_damage: float
    skill_id: Optional[int]
    pet_id: Optional[int]
    boss_items: List[int]
    image: Optional[str]
    xp_reward: int
    reward_role_id: Optional[int]

class BossCalculator(ProfileCalculator):
    def __init__(self, boss: Boss) -> None:
        self.profile = boss
        self.items = items.items_by_ids(boss.boss_items)
        self.pet = items.item_by_id(boss.pet_id) if boss.pet_id is not None else None
        self.skill = items.item_by_id(boss.skill_id) if boss.skill_id is not None else None

class BossError(Exception):
    ...

class Bosses():
    bosses: Dict[str, Boss] = dict()
    def __init__(self, bosses_path: str) -> None:
        try:
            with open(bosses_path, "r", encoding="utf-8") as json_bosses:
                for key, value in load(json_bosses).items():
                    boss_fields = {field.name: value.get(field.name) for field in fields(Boss)}
                    boss_fields["boss_id"] = key
                    if boss_fields["boss_items"] is None:
                        boss_fields["boss_items"] = list()
                    self.bosses.setdefault(key, Boss(**boss_fields))
        except Exception:
            raise BossError(f"Bosses file at {bosses_path} is invalid or not found")
    
    def get_boss(self, boss_id: str) -> Boss:
        boss_data = self.bosses.get(boss_id)
        if boss_data is None:
            raise BossError(f"Boss with id {boss_id} is invalid or not found")
        return boss_data
    
    @property
    def all_bosses(self) -> List[Boss]:
        return self.bosses.values()
        

bosses = Bosses(settings.get_config("BOSSES_PATH"))