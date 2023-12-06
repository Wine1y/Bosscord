from nextcord.ext.commands import Cog

from db.base import database
from bot.modules import Module


class GeneralModule(Module):

    @Cog.listener()
    async def on_ready(self):
        await database.connect()
        client_user = self.client.user
        print(f"Connected as {client_user.name}#{client_user.discriminator}, DB: {database.url}")