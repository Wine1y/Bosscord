from typing import Callable, List, Optional
from nextcord import slash_command, Embed, Colour, Member
from nextcord.ext.commands import Bot
from sqlalchemy.engine.row import Row

from core.texts import texts
from core.items import ActiveItemEffect, ActiveEffectType


class NotInlineEmbedField():
    value: str
    def __init__(self, value: str) -> None:
        self.value = value

def localized_slash_command(command_name: str):

    def decorator(func: Callable):
        descriptions = texts.get_command_descriptions(command_name)
        return slash_command(
            description=descriptions.get("en-US"),
            description_localizations=descriptions
        )(func)
    
    return decorator

def get_embed(
    embed_name: str,
    field_values: Optional[List[str]]=None,
    embed_title: Optional[str]=None,
    thumbnail: Optional[str]=None,
    inline:bool=True
) -> Embed:
    embed_data = texts.get_embed_data(embed_name)
    field_titles = embed_data.get("fields")
    
    if embed_title is None:
        embed_title = embed_data.get("title")

    embed = Embed(
        title=embed_title,
        colour=Colour.from_rgb(*embed_data.get("color_rgb")),
        description=embed_data.get("description")
    )

    if thumbnail is not None:
        embed.set_thumbnail(thumbnail)

    if field_values is None:
        return embed

    for i in range(len(field_values)):
        if i < len(field_titles):
            field_value = field_values[i]
            if type(field_value) is NotInlineEmbedField:
                embed.add_field(name=field_titles[i], value=field_value.value, inline=False)
            else:
                embed.add_field(name=field_titles[i], value=str(field_value), inline=inline)
    return embed

def effect_to_string(effect: ActiveItemEffect) -> str:
    effect_strings = {
        ActiveEffectType.HEAL: r"heals **`%amount%`** hitpoints",
        ActiveEffectType.DAMAGE: r"deals **`%amount%`** damage",
        ActiveEffectType.DISABLE_PET: r"disables enemy pet",
        ActiveEffectType.DISABLE_SKILL: r"disables an opponents skill",
        ActiveEffectType.DISARM: r"removes a random weapon from opponent"
    }

    all_strings = [
        effect_strings.get(effect_data.type).replace(r"%amount%", str(effect_data.amount))
        for effect_data in effect.effects
        ]

    return ", ".join(all_strings).capitalize()

def get_profile_item_ids(profile: Row) -> List[str]:
    profile_item_ids = profile.user_items.split(",")
    if len(profile_item_ids[0]) > 0:
        profile_item_ids = [item_id for item_id in profile_item_ids]
    else:
        profile_item_ids = list()
    return profile_item_ids

def get_progress_bar_text(value: int, max_value: int, letters: int, fill_empty_space: bool=True):
    percentage = value/max_value
    progress_letters = round(letters*percentage)
    empty_filler = "—" if fill_empty_space else "⠀"
    return "".join(["▇"if i <= progress_letters else empty_filler for i in range(1, letters+1)])

async def give_role(member: Member, role_id: int) -> None:
    if member.get_role(role_id) is not None: return
    role = member.guild.get_role(role_id)
    if role is None: return
    await member.add_roles(role, reason="RPG Reward")