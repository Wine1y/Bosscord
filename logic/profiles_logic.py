from nextcord import Embed, Member
from typing import Optional, List
from sqlalchemy.engine.row import Row
from datetime import datetime

from bot.utils import (get_embed, get_profile_item_ids, effect_to_string,
                       NotInlineEmbedField, get_progress_bar_text, give_role)
from core.settings import settings
from core.texts import texts
from core.items import items, ItemType, Item, PassiveItemEffect
from db.repositories.profile import UserProfileRepository


class ProfileCalculator():
    profile: Row
    items: List[Item]
    pet: Optional[Item]
    skill: Optional[Item]

    def __init__(self, profile: Row) -> None:
        self.profile = profile
        self.items = items.items_by_ids(get_profile_item_ids(profile))
        self.pet = items.item_by_id(profile.pet_id) if profile.pet_id is not None else None
        self.skill = items.item_by_id(profile.skill_id) if profile.skill_id is not None else None

    @property
    def passive_effects(self) -> List[PassiveItemEffect]:
        effects = [
            item.passive_effect
            for item in self.items
            if item.passive_effect is not None
        ]
        return effects

    @property
    def health(self) -> int:
        total_boost = sum([boost.health_boost for boost in self.passive_effects if boost.health_boost is not None])
        return self.profile.hp+total_boost
    
    @property
    def attack(self) -> int:
        total_boost = sum([boost.attack_boost for boost in self.passive_effects if boost.attack_boost is not None])
        return self.profile.attack+total_boost
    
    @property
    def armor(self) -> float:
        total_boost = sum([boost.armor_boost for boost in self.passive_effects if boost.armor_boost is not None])
        return min(self.profile.armor+total_boost, 100.0)
    
    @property
    def crit_chance(self) -> float:
        total_boost = sum([boost.crit_chance_boost for boost in self.passive_effects if boost.crit_chance_boost is not None])
        return self.profile.crit_chance+total_boost
    
    @property
    def crit_damage(self) -> float:
        total_boost = sum([boost.crit_damage_boost for boost in self.passive_effects if boost.crit_damage_boost is not None])
        return self.profile.crit_damage+total_boost


async def get_profile_embed(member: Member) -> Optional[Embed]:
    user_profile = await UserProfileRepository().get_by_discord_id(member.id)
    if user_profile is None:
        return None
    calculator = ProfileCalculator(user_profile)
    embed_title = texts.get_embed_data("profile").get("title").replace(r"%username%", user_profile.name)
    armors = [item for item in calculator.items if item.type is ItemType.ARMOR]
    weapons = [item for item in calculator.items if item.type is ItemType.WEAPON]

    if user_profile.lvl < settings.get_config("MAX_LVL"):
        xp_to_lvlup = settings.get_level_data(user_profile.lvl+1)["xp_needed"]
        xp_info = NotInlineEmbedField(f"`{get_progress_bar_text(user_profile.xp, xp_to_lvlup, 30, False)}` **`{user_profile.xp}/{xp_to_lvlup}`**")
    else:
        xp_info = NotInlineEmbedField("You have reached max lvl")

    embed_values = [
        datetime.strptime(user_profile.created_at, r"%Y-%m-%d %H:%M:%S.%f").strftime(r"%d.%m.%y") ,
        user_profile.lvl,
        calculator.health,
        calculator.attack,
        f"{calculator.armor}%",
        f"{calculator.crit_chance}%",
        f"x{calculator.crit_damage}",
        items.item_by_id(user_profile.skill_id).name if user_profile.skill_id is not None else "None",
        items.item_by_id(user_profile.pet_id).name if user_profile.pet_id is not None else "None",
        "\n".join([f"-{item.name} (**`{item.passive_effect.armor_boost}%`**)" for item in armors]) if len(armors) > 0 else "None",
        "\n".join([f"-{item.name} (**`+{item.passive_effect.attack_boost}`**)" for item in weapons]) if len(weapons) > 0 else "None",
        xp_info
    ]
    embed = get_embed("profile", embed_values, embed_title, thumbnail=member.display_avatar.url)
    return embed

async def get_skill_embed(member: Member) -> Optional[Embed]:
    user_profile = await UserProfileRepository().get_by_discord_id(member.id)
    if user_profile is None:
        return None
    embed_title = texts.get_embed_data("skill").get("title").replace(r"%username%", user_profile.name)
    skill = items.item_by_id(user_profile.skill_id) if user_profile.skill_id is not None else None
    skill_image = skill.image if skill is not None else None
    embed_values = [f"{skill.name}" if skill is not None else "None"]
    if skill is not None:
        embed_values.append(effect_to_string(skill.active_effect))
    embed = get_embed(
        "skill",
        embed_values,
        embed_title,
        thumbnail=skill_image,
        inline=False
    )
    return embed

async def get_pet_embed(member: Member) -> Optional[Embed]:
    user_profile = await UserProfileRepository().get_by_discord_id(member.id)
    if user_profile is None:
        return None
    embed_title = texts.get_embed_data("pet").get("title").replace(r"%username%", user_profile.name)
    pet = items.item_by_id(user_profile.pet_id) if user_profile.pet_id is not None else None
    pet_image = pet.image if pet is not None else None
    embed_values = [f"{pet.name}" if pet is not None else "None"]
    if pet is not None:
        embed_values.append(effect_to_string(pet.active_effect))
    embed = get_embed(
        "pet",
        embed_values,
        embed_title,
        thumbnail=pet_image,
        inline=False
    )
    return embed

async def get_armor_embed(member: Member) -> Optional[Embed]:
    user_profile = await UserProfileRepository().get_by_discord_id(member.id)
    if user_profile is None:
        return None
    embed_title = texts.get_embed_data("armor").get("title").replace(r"%username%", user_profile.name)
    user_items = items.items_by_ids(get_profile_item_ids(user_profile))
    user_armors = [item for item in user_items if item.type is ItemType.ARMOR]
    embed_values = ["\n".join([f"-{armor.name} (**`{armor.passive_effect.armor_boost}%`** damage reduction)" for armor in user_armors])]
    if len(embed_values) < 1:
        embed_values = ["None"]
    embed = get_embed("armor", embed_values, embed_title)
    return embed

async def get_weapon_embed(member: Member) -> Optional[Embed]:
    user_profile = await UserProfileRepository().get_by_discord_id(member.id)
    if user_profile is None:
        return None
    embed_title = texts.get_embed_data("weapon").get("title").replace(r"%username%", user_profile.name)
    user_items = items.items_by_ids(get_profile_item_ids(user_profile))
    user_weapons = [item for item in user_items if item.type is ItemType.WEAPON]
    embed_values = ["\n".join([f"-{weapon.name} (**`+{weapon.passive_effect.attack_boost}`** attack)" for weapon in user_weapons])]
    if len(embed_values) < 1:
        embed_values = ["None"]
    embed = get_embed("weapon", embed_values, embed_title)
    return embed

async def gain_xp(profile: Row, xp_amount: int, member: Member) -> None:
    if profile.lvl >= settings.get_config("MAX_LVL"):
        return
    new_level_data = settings.get_level_data(profile.lvl+1)
    xp_needed = new_level_data["xp_needed"]
    to_lvl_up = xp_needed-profile.xp
    if xp_amount >= to_lvl_up:
        await UserProfileRepository().update(profile.id, lvl=profile.lvl+1, xp=xp_amount-to_lvl_up, **new_level_data["stats"])
        reward_role_id = new_level_data.get("reward_role_id")
        if reward_role_id is not None:
            await give_role(member, reward_role_id)
    else:
        await UserProfileRepository().update(profile.id, xp=profile.xp+xp_amount)