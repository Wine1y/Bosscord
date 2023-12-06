from sqlalchemy import Column, String, Integer, Float
from nextcord import Member

from db.base import BaseModel
from core.settings import settings

class UserProfile(BaseModel):
    __tablename__ = "profiles"

    discord_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    lvl = Column(Integer, nullable=False)
    xp = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    armor = Column(Float, nullable=False) #PERCENTS
    crit_chance = Column(Float, nullable=False) #PERCENTS
    crit_damage = Column(Float, nullable=False) #MULTIPLIER (x1.2)
    skill_id = Column(String, nullable=True)
    pet_id = Column(String, nullable=True)
    user_items = Column(String, nullable=False)

    @classmethod
    def new_profile_for_member(cls, member: Member) -> "UserProfile":
        start_stats = settings.get_config("START_STATS")
        return cls(
            discord_id=member.id,
            name=member.display_name,
            lvl=start_stats["lvl"],
            xp=start_stats["xp"],
            hp=start_stats["hp"],
            attack=start_stats["attack"],
            armor=float(start_stats["armor"]),
            crit_chance=float(start_stats["crit_chance"]),
            crit_damage=float(start_stats["crit_damage"]),
            skill_id=start_stats["skill_id"],
            pet_id=start_stats["pet_id"],
            user_items=start_stats["items"]
        )