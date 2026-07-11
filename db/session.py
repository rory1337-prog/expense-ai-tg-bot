from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

if DATABASE_URL.startswith("sqlite:///"):
    db_file = DATABASE_URL.replace("sqlite:///", "")
    db_path = Path(db_file)

    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
