from db.base import BASE, engine, database
from db.models import profile

BASE.metadata.create_all(bind=engine)