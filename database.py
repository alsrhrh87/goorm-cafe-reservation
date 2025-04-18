from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

DATABASE_URL = "sqlite:///./reservations.db"

# ✅ 이 줄이 create_table.py에서 필요함!
engine = create_engine(DATABASE_URL)
metadata = MetaData()

database = Database(DATABASE_URL)

reservations = Table(
    "reservations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("phone", String(100)),
    Column("time", String(100)),
    Column("drink", String(100)),
    Column("inquiry", String(255))
)