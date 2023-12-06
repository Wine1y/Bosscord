from nextcord import Member
from typing import Tuple, Optional
import aiohttp
from json import dumps

from core.settings import settings

HEADERS = {"Authorization": settings.get_config("UNB_BOT_TOKEN")}

async def get_member_balance(member: Member) -> Optional[Tuple[int, int]]:
    guild_id, user_id = member.guild.id, member.id
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            async with session.get(
                f"https://unbelievaboat.com/api/v1/guilds/{guild_id}/users/{user_id}"
            ) as resp:
                if resp.status != 200:
                    return None
                resp_json = await resp.json()
                return (resp_json.get("cash"), resp_json.get("bank"))
        except:
            return None

async def patch_member_balance(member: Member, amount: int, reason: str) -> bool:
    guild_id, user_id = member.guild.id, member.id
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            async with session.patch(
                f"https://unbelievaboat.com/api/v1/guilds/{guild_id}/users/{user_id}",
                data=dumps({"cash": amount, "bank": 0, "reason": reason})
            ) as resp:
                if resp.status != 200:
                    print(await resp.text())
                    return False
                else:
                    return True
        except Exception as e:
            print(repr(e))
            return False