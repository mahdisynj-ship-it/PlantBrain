import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "data" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_URL = (
    f"sqlite:///{DATABASE_DIR / 'plantbrain.db'}"
)

DATABASE_URL = os.getenv(
    "PLANTBRAIN_DATABASE_URL",
    DEFAULT_DATABASE_URL,
)


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(
    dbapi_connection,
    connection_record,
):
    cursor = dbapi_connection.cursor()

    try:
        cursor.execute(
            "PRAGMA foreign_keys=ON"
        )
    finally:
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)