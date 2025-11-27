# backend/app/database.py
import os
from sqlalchemy import MetaData
from databases import Database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.example"))

DATABASE_URL = os.getenv("DATABASE_URL")  # expects asyncpg URL

# databases Database (async) and SQLAlchemy engine (sync) for create_all
database = Database(DATABASE_URL)

# SQLAlchemy Base and engine (sync) for metadata create
from sqlalchemy import engine_from_config
from sqlalchemy import create_engine as create_sync_engine

# synchronous engine for metadata operations (create tables)
sync_database_url = DATABASE_URL.replace("+asyncpg", "") if DATABASE_URL else None
engine = create_sync_engine(sync_database_url, future=True) if sync_database_url else None

metadata = MetaData()
Base = declarative_base(metadata=metadata)
