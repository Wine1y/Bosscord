from sqlalchemy import select
from sqlalchemy.engine.row import Row
from typing import Optional, List

from db.repositories.repository import Repository
from db.models.profile import UserProfile
from db.base import database


class UserProfileRepository(Repository):
    repository_object = UserProfile

    async def get_used_discord_ids(self):
        query = select((self.table.c.discord_id))
        return await database.fetch_all(query.__str__())
    
    async def get_by_discord_id(self, discord_id: int) -> Optional[Row]:
        query = select(self.table).where(self.table.c.discord_id==discord_id)
        return await database.fetch_one(query.__str__(), values={"discord_id_1": discord_id})
    
