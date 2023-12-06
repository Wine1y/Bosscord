from nextcord import Intents
from nextcord.ext.commands import Bot

from core.settings import settings
from bot.modules import load_modules


def run_bot():
    intents = Intents.default()
    intents.members = True
    intents.message_content = True

    client = Bot(
        command_prefix=settings.get_config("COMMAND_PREFIX"),
        intents=intents,
        default_guild_ids=settings.get_config("WORKING_GUILDS")
    )
    client.remove_command('help')
    load_modules(client)

    client.run(settings.get_config("BOT_TOKEN"))


