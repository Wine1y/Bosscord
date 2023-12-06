from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, TIMESTAMP, create_engine
from databases import Database
from datetime import datetime

from core.settings import settings


BASE = declarative_base()

engine = create_engine(settings.get_config("DB_URL"))
database  = Database(settings.get_config("DB_URL"))

class BaseModel(BASE):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)