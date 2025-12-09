from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# backend/app/config.py

MYSQL_USER = "root"
MYSQL_PASSWORD = "Manoakil@12"
MYSQL_HOST = "localhost"
MYSQL_DB = "mil_asset_system"

DATABASE_URL = (
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
