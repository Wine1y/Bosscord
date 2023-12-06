from sqlalchemy.engine.row import Row
from typing import List, Union, Optional, Callable
from nextcord.ext.commands import Bot
from nextcord import Interaction, Embed, Colour
from dataclasses import dataclass
from random import randint, choice
from asyncio import sleep

from core.bosses import Boss, BossCalculator
from core.items import items, Item, ItemType, ActiveEffectType
from core.texts import texts
from core.settings import settings
from logic.profiles_logic import ProfileCalculator
from bot.utils import get_progress_bar_text, effect_to_string


@dataclass
class Fighter():
    profile: Row
    current_hp: int
    max_hp: int
    current_attack: int
    current_armor: float
    current_crit_chance: float
    current_crit_damage: float
    skill: Optional[Item]
    pet: Optional[Item]
    items: List[Item]
    enemy: "Fighter"
    used_items = dict()

    @classmethod
    def from_user(cls, user: Row) -> "Fighter":
        calculator = ProfileCalculator(user)
        return cls(
            user, calculator.health, calculator.health, calculator.attack, calculator.armor,
            calculator.crit_chance,calculator.crit_damage, calculator.skill, calculator.pet,
            calculator.items, None
        )
    
    def use_item(self, item: Item) -> bool:
        item_max_uses = item.active_effect.max_uses_per_battle
        if item_max_uses is not None:
            item_uses_counter = self.used_items.get(item.id, 0)
            if item_uses_counter >= item_max_uses:
                return False
        if randint(0,100) < item.active_effect.interception_rate:
            for effect in item.active_effect.effects:
                
                if effect.type is ActiveEffectType.HEAL:
                    if self.current_hp >= self.max_hp:
                        return False
                    self.heal(effect.amount)
                elif effect.type is ActiveEffectType.DAMAGE:
                    if self.enemy.current_hp <= 0:
                        return False
                    self.enemy.take_damage(effect.amount)
                elif effect.type is ActiveEffectType.DISABLE_PET:
                    if self.enemy.pet is None:
                        return False
                    self.enemy.disable_pet()
                elif effect.type is ActiveEffectType.DISABLE_SKILL:
                    if self.enemy.skill is None:
                        return False
                    self.enemy.disable_skill()
                elif effect.type is ActiveEffectType.DISARM:
                    enemy_weapons = [weapon for weapon in self.enemy.items if weapon.type is ItemType.WEAPON]
                    if len(enemy_weapons) <= 0:
                        return False
                    self.enemy.disarm()

            if item_max_uses is not None:
                self.used_items.setdefault(item.id, self.used_items.get(item.id, 0)+1)
            return True

    def heal(self, amount: int) -> None:
        new_health = self.current_hp+amount
        self.current_hp = min(new_health, self.max_hp)
    
    def take_damage(self, damage: int) -> int:
        absorption = self.current_armor/100
        damage_dealed = round(damage-(damage*absorption))
        if damage_dealed > self.current_hp:
            damage_dealed = self.current_hp
        self.current_hp = self.current_hp-damage_dealed
        return damage_dealed
    
    def disable_pet(self) -> None:
        self.pet = None
    
    def disable_skill(self) -> None:
        self.skill = None
    
    def disarm(self) -> None:
        weapon_indexes = [i for i in range(len(self.items)) if self.items[i].type == ItemType.WEAPON]
        self.items.pop(choice(weapon_indexes))

    async def your_turn(self, new_move: Callable) -> None:
        active_items = [item for item in [self.skill, self.pet] if item is not None and item.active_effect is not None]
        for item in active_items:
            if self.use_item(item):
                await new_move(f"**{self.profile.name}** uses **{item.name}** and {effect_to_string(item.active_effect)}")
        if self.enemy.current_hp <= 0:
            return
        is_crit = False
        if randint(0, 100) < self.current_crit_chance:
            is_crit = True
            damage = round(self.current_attack*self.current_crit_damage)
        else:
            damage = self.current_attack
        damage_dealed = self.enemy.take_damage(damage)
        await new_move(f"**{self.profile.name}** attacks **{self.enemy.profile.name}** and deals **`{damage_dealed}`** damage {'**(CRITICAL)**' if is_crit else ''}")

@dataclass
class FightStatus():
    fighters: List[Fighter]
    interaction: Interaction
    client: Bot
    inside_move_delay=settings.get_config("MOVE_DELAY")
    last_move: Optional[str]=None
    current_turn=0
    turns_passed=0

    @classmethod
    def create_pvp_fight(
        cls,
        user_1: Row,
        user_2: Row,
        interaction: Interaction,
        client: Bot,
    ):
        user_1_fighter = Fighter.from_user(user_1)
        user_2_fighter = Fighter.from_user(user_2)

        user_1_fighter.enemy = user_2_fighter
        user_2_fighter.enemy = user_1_fighter

        fighters = [user_1_fighter, user_2_fighter]

        return cls(fighters, interaction, client)

    async def next_turn(self) -> Optional[Fighter]:
        await self.fighters[self.current_turn].your_turn(self.new_move)
        if self.fighters[0].current_hp <= 0:
            return self.fighters[1]
        elif self.fighters[1].current_hp <= 0:
            return self.fighters[0]

        if self.current_turn+1 >= len(self.fighters):
            self.current_turn = 0
        else:
            self.current_turn+=1
        self.turns_passed+=1
    
    async def new_move(self, move: str) -> None:
        self.last_move = move
        await self.update_embed()
        await sleep(self.inside_move_delay)
    
    async def update_embed(self, winner: Optional[Fighter]=None):
        embed = self.to_embed(winner)
        if winner is None:
            await self.interaction.edit_original_message(embed=embed)
        else:
            await self.interaction.delete_original_message()
            await self.interaction.send(embed=embed, ephemeral=False)

    def to_embed(self, winner: Optional[Fighter]=None) -> Embed:
        turn_owner = self.fighters[self.current_turn].profile.name
        turn_number = self.turns_passed+1

        embed_data = texts.get_embed_data("fight")
        embed = Embed(
            title=embed_data.get("title")
                            .replace(r"%fighter1%", self.fighters[0].profile.name)
                            .replace(r"%fighter2%", self.fighters[1].profile.name),
            colour=Colour.from_rgb(*embed_data.get("color_rgb")),
            description=embed_data.get("description")
        )
        if winner is not None:
            embed.add_field(name="Result", value=f"**{winner.profile.name}** won in **`{self.turns_passed+1}`** turns")
            member = self.interaction.guild.get_member(winner.profile.discord_id)
            if member is not None:
                embed.set_thumbnail(member.display_avatar.url)
            return embed

        embed.add_field(name="Turn", value=turn_owner)
        embed.add_field(name="Turn №", value=str(turn_number))
        for fighter in self.fighters:
            embed.add_field(
                name=f"{fighter.profile.name} (Attack: **`{fighter.current_attack}`**, Armor: **`{fighter.current_armor}%`**)",
                value=f"[{get_progress_bar_text(fighter.current_hp, fighter.max_hp, 15)}] {fighter.current_hp}/{fighter.max_hp} hp",
                inline=False
                )
        if self.last_move is not None:
            embed.add_field(name="Move", value=self.last_move, inline=False)

        current_fighter = self.fighters[self.current_turn]
        member = self.interaction.guild.get_member(current_fighter.profile.discord_id)
        if member is not None:
            turn_image = member.display_avatar.url
        else:
            turn_image = None
        embed.set_thumbnail(turn_image)
        return embed

class PvpFight():
    fight_status: FightStatus
    bot_client: Bot

    def __init__(self, user_1: Row, user_2: Row, client: Bot, interaction: Interaction) -> None:
        self.fight_status = FightStatus.create_pvp_fight(user_1, user_2, interaction, client)
        self.bot_client = client
    
    async def get_battle_winner(self) -> Fighter:
        turn_delay_seconds = settings.get_config("TURN_DELAY")
        await self.fight_status.update_embed()
        while True:
            winner = await self.fight_status.next_turn()
            if winner is not None:
                await self.fight_status.update_embed(winner=winner)
                return winner
            else:
                await sleep(turn_delay_seconds)