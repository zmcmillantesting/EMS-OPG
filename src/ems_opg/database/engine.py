from pathlib import Path
from sqlalchemy import create_engine
from src.ems_opg.core.paths_manager import PathManager
from src.ems_opg.core.constants import DEFAULT_DATABASE_NAME, DB_DIR

DB_DIR = PathManager().database  # Use PathManager to get the database directory
DB_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the database directory exists

DATABASE_FILE = DB_DIR / DEFAULT_DATABASE_NAME
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(DATABASE_URL, echo=True, future=True)
