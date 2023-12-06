from nextcord import Interaction, SlashOption, User, Member

from bot.modules import Module
from bot.utils import localized_slash_command
from logic.shop_logic import get_shop_embed, buy_item
from core.items import items

class ShopModule(Module):

    @localized_slash_command("shop")
    async def shop(self, interaction: Interaction):
        await interaction.send(ephemeral=False, embed=get_shop_embed())
    
    @localized_slash_command("buy_skill")
    async def buy_skill(
        self,
        interaction: Interaction,
        item_id: str = SlashOption(choices={item.name: item.id for item in items.skills})
    ):
        await interaction.response.defer(ephemeral=True)
        buy_result = await buy_item(interaction.user, items.item_by_id(item_id))
        await interaction.followup.send(buy_result)
    
    @localized_slash_command("buy_pet")
    async def buy_pet(
        self,
        interaction: Interaction,
        item_id: str = SlashOption(choices={item.name: item.id for item in items.pets})
    ):
        await interaction.response.defer(ephemeral=True)
        buy_result = await buy_item(interaction.user, items.item_by_id(item_id))
        await interaction.followup.send(buy_result)
    
    @localized_slash_command("buy_armor")
    async def buy_armor(
        self,
        interaction: Interaction,
        item_id: str = SlashOption(choices={item.name: item.id for item in items.armors})
    ):
        await interaction.response.defer(ephemeral=True)
        buy_result = await buy_item(interaction.user, items.item_by_id(item_id))
        await interaction.followup.send(buy_result)
    
    @localized_slash_command("buy_weapon")
    async def buy_weapon(
        self,
        interaction: Interaction,
        item_id: str = SlashOption(choices={item.name: item.id for item in items.weapons})
    ):
        await interaction.response.defer(ephemeral=True)
        buy_result = await buy_item(interaction.user, items.item_by_id(item_id))
        await interaction.followup.send(buy_result)
        

    
