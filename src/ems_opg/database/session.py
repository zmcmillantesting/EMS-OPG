from sqlalchemy.orm import sessionmaker
from src.ems_opg.database.engine import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)