from nextcord import Embed, Member

from bot.utils import get_embed, effect_to_string, get_profile_item_ids
from core.items import items, Item, ItemType
from core.settings import settings
from core.texts import texts
from db.repositories.profile import UserProfileRepository
from logic.unb_logic import get_member_balance, patch_member_balance


def get_shop_embed() -> Embed:
    currency = settings.get_config("CURRENCY_SYMBOL")
    skills, pets = items.skills, items.pets, 
    armors, weapons = items.armors, items.weapons

    skills_values = [
        f"-**{skill.name}**: {effect_to_string(skill.active_effect)} - **`{skill.price}{currency}`**"
        +(f" (Level {skill.required_level} required)" if skill.required_level is not None else "")
        for skill in skills
    ]

    pets_values = [
        f"-**{pet.name}**: {effect_to_string(pet.active_effect)} - **`{pet.price}{currency}`**"
        +(f" (Level {pet.required_level} required)" if pet.required_level is not None else "")
        for pet in pets
    ]

    armors_values = [
        f"-**{armor.name}**: **`+{armor.passive_effect.armor_boost}%`** damage reduction - **`{armor.price}{currency}`**"
        +(f" (Level {armor.required_level} required)" if armor.required_level is not None else "")
        for armor in armors
    ]

    weapons_values = [
        f"-**{weapon.name}**: **`+{weapon.passive_effect.attack_boost}`** to damage - **`{weapon.price}{currency}`**"
        +(f" (Level {weapon.required_level} required)" if weapon.required_level is not None else "")
        for weapon in weapons
    ]

    embed = get_embed(
        "shop",
        [
            "\n".join(skills_values),
            "\n".join(pets_values),
            "\n".join(armors_values),
            "\n".join(weapons_values)
        ],
        inline=False
    )
    return embed

async def buy_item(member: Member, item: Item) -> str:
    item_type = item.type
    user_rep = UserProfileRepository()
    member_stats = await user_rep.get_by_discord_id(member.id)
    if member_stats is None:
        return texts.get_error_text("GENERAL_ERROR")
    if item.required_level is not None and member_stats.lvl < item.required_level:
        return texts.get_error_text("LEVEL_TOO_LOW")

    member_item_ids = get_profile_item_ids(member_stats)

    if item_type is ItemType.PET and member_stats.pet_id == item.id:
        return texts.get_error_text("ITEM_ALREADY_PURCHASED")
    elif item_type is ItemType.SKILL and member_stats.skill_id == item.id:
        return texts.get_error_text("ITEM_ALREADY_PURCHASED")
    elif item.id in member_item_ids:
        return texts.get_error_text("ITEM_ALREADY_PURCHASED")

    member_balance = await get_member_balance(member)
    if member_balance is None:
        return texts.get_error_text("GENERAL_ERROR")
    if member_balance[0] < item.price:
        return texts.get_error_text("INSUFFICIENT_FUNDS")
    
    buy_result = await patch_member_balance(member, -item.price, f"User bought {item.name}")
    if not buy_result:
        return texts.get_error_text("GENERAL_ERROR")

    if item_type is ItemType.PET:
        update_result = await user_rep.update(member_stats.id, pet_id=item.id)
    elif item_type is ItemType.SKILL:
        update_result = await user_rep.update(member_stats.id, skill_id=item.id)
    else:
        member_item_ids.append(item.id)
        update_result = await user_rep.update(member_stats.id, user_items=",".join([str(item_id) for item_id in member_item_ids]))
    if not update_result:
        await patch_member_balance(member, item.price, f"Refund for {item.name}")
        return texts.get_error_text("GENERAL_ERROR")
    return texts.get_message_text("PURCHASED").replace(r"%itemname%", item.name)