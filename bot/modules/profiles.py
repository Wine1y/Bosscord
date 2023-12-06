from nextcord.ext.commands import Cog
from nextcord import Interaction, SlashOption, Member, User
from typing import Optional

from bot.modules import Module
from bot.utils import localized_slash_command
from core.settings import settings
from core.texts import texts
from db.models.profile import UserProfile
from db.repositories.profile import UserProfileRepository
from logic.profiles_logic import (
    get_profile_embed, get_skill_embed, 
    get_pet_embed, get_armor_embed,
    get_weapon_embed)


class ProfilesModule(Module):
    
    @Cog.listener()
    async def on_ready(self):
        profile_rep = UserProfileRepository()
        used_ids = {profile.discord_id: True for profile in await profile_rep.get_used_discord_ids()}
        for guild_id in settings.get_config("WORKING_GUILDS"):
            guild = self.client.get_guild(guild_id)
            if guild is None:
                continue

            for member in guild.members:
                if not member.bot and used_ids.get(member.id) is None:
                    await profile_rep.insert(UserProfile.new_profile_for_member(member))
    
    @Cog.listener()
    async def on_member_join(self, member: Member):
        if member.bot:
            return
        profile_rep = UserProfileRepository()
        user_profile = await profile_rep.get_by_discord_id(member.id)
        if user_profile is not None:
            return
        await profile_rep.insert(UserProfile.new_profile_for_member(member))
    
    @localized_slash_command("profile")
    async def profile(
        self,
        interaction: Interaction,
        member: Optional[Member] = SlashOption(required=False)
    ):
        if member is None:
            member = interaction.user
        embed = await get_profile_embed(member)
        if embed is not None:
            await interaction.send(ephemeral=False, embed=embed)
        else:
            await interaction.send(texts.get_error_text("GENERAL_ERROR"), ephemeral=True)
    
    @localized_slash_command("skill")
    async def skill(
        self,
        interaction: Interaction,
    ):
        await interaction.send(ephemeral=True, embed=await get_skill_embed(interaction.user))
    
    @localized_slash_command("pet")
    async def pet(
        self,
        interaction: Interaction,
    ):
        await interaction.send(ephemeral=True, embed=await get_pet_embed(interaction.user))
    
    @localized_slash_command("armor")
    async def armor(
        self,
        interaction: Interaction,
    ):
        await interaction.send(ephemeral=True, embed=await get_armor_embed(interaction.user))
    
    @localized_slash_command("weapon")
    async def weapon(
        self,
        interaction: Interaction,
    ):
        await interaction.send(ephemeral=True, embed=await get_weapon_embed(interaction.user))