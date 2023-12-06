from abc import ABC
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.engine.row import Row
from sqlalchemy import insert, select, update
from typing import Optional, List
from datetime import datetime


from db.base import database

class Repository(ABC):
    repository_object: DeclarativeMeta

    @property
    def table(self):
        return self.repository_object.__table__

    async def get(self, id: int) -> Optional[Row]:
        query = select(self.table).where(self.table.c.id==id)
        return await database.fetch_one(query.__str__(), values={"id_1": id})

    async def get_all(self) -> List[object]:
        query = select(self.table)
        return await database.fetch_all(query.__str__())

    async def insert(self, item: object) -> bool:
        try:
            values = {column.name: getattr(item, column.name) for column in item.__table__.columns}
            values["created_at"] = datetime.utcnow()
            query = insert(self.table).values(**values)
            await database.execute(query.__str__(), values=values)
            return True
        except:
            return False
    
    async def update(self, id: int, **updated_fields) -> bool:
        try:
            query = update(self.table).where(self.table.c.id==id).values(**updated_fields)
            updated_fields["id_1"] = id
            await database.execute(query.__str__(), values=updated_fields)
            return True
        except:
            return False