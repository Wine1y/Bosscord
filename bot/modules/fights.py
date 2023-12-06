from nextcord import Interaction, SlashOption, Member, User
from sqlalchemy.engine.row import Row

from bot.modules import Module
from bot.utils import localized_slash_command, give_role
from core.bosses import bosses
from core.texts import texts
from core.settings import settings
from db.repositories.profile import UserProfileRepository
from logic.bossfight_logic import BossFight
from logic.pvp_logic import PvpFight
from logic.profiles_logic import gain_xp

class FightModule(Module):
    
    @localized_slash_command("boss")
    async def boss(
        self,
        interaction: Interaction,
        boss_id: str = SlashOption(choices={boss.name: boss.boss_id for boss in bosses.all_bosses})
    ):
        user_rep = UserProfileRepository()
        user = await user_rep.get_by_discord_id(interaction.user.id)
        boss = bosses.get_boss(boss_id)
        await interaction.response.defer(ephemeral=True)
        boss_fight = BossFight(user, boss, self.client, interaction)
        winner = await boss_fight.get_battle_winner()
        if type(winner.profile) is Row and boss.xp_reward is not None:
            await gain_xp(winner.profile, boss.xp_reward, interaction.user)
            if boss.reward_role_id is not None:
                if interaction.user is User:
                    await give_role(interaction.guild.get_member(interaction.user.id), boss.reward_role_id)
                else:
                    await give_role(interaction.user, boss.reward_role_id)
    
    @localized_slash_command("pvp")
    async def pvp(
        self,
        interaction: Interaction,
        member: Member = SlashOption()
    ):
        if member.bot:
            await interaction.send(texts.get_error_text("PVP_ON_BOT"), ephemeral=True)
            return  
        if interaction.user.id == member.id:
            await interaction.send(texts.get_error_text("PVP_ON_SELF"), ephemeral=True)
            return
            
        user_rep = UserProfileRepository()
        user_1 = await user_rep.get_by_discord_id(interaction.user.id)
        user_2 = await user_rep.get_by_discord_id(member.id)    
        if user_1 is None or user_2 is None:
            await interaction.send(texts.get_error_text("GENERAL_ERROR"), ephemeral=True)  
        await interaction.response.defer(ephemeral=True)  
        pvp_fight = PvpFight(user_1, user_2, self.client, interaction)
        winner = await pvp_fight.get_battle_winner()
        await gain_xp(winner.profile, settings.get_config("PVP_XP_REWARD"), interaction.user)