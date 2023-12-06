from nextcord.ext.commands import Bot, Cog

class Module(Cog):
    client: Bot

    def __init__(self, client: Bot) -> None:
        self.client = client
        super().__init__()

from bot.modules.general import GeneralModule
from bot.modules.profiles import ProfilesModule
from bot.modules.shop import ShopModule
from bot.modules.fights import FightModule

MODULES = [GeneralModule, ProfilesModule, ShopModule, FightModule]

def load_modules(client: Bot):
    for module in MODULES:
        client.add_cog(module(client))

