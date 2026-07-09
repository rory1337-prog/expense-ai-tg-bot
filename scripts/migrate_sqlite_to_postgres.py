import os
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import DATABASE_URL
from db.models import Entry, UserSettings

SQLITE_DB = Path(os.getenv("SQLITE_DB", "expenses.db"))

def migrate():
    if not SQLITE_DB.exists():
        raise FileNotFoundError(f"SQLite database not found: {SQLITE_DB}")
    print("SQLite:", SQLITE_DB.resolve())
    print("Postgres:", DATABASE_URL)
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        entries = sqlite_conn.execute("SELECT * FROM entries").fetchall()
        for row in entries:
            session.merge(
                Entry(
                    id=row["id"],
                    chat_id=str(row["chat_id"]),
                    name=row["name"],
                    amount=row["amount"],
                    category=row["category"],
                    type=row["type"],
                    created_at=row["created_at"],
                )
            )
        settings = sqlite_conn.execute("SELECT * FROM user_settings").fetchall()
        for row in settings:
            session.merge(
                UserSettings(
                    chat_id=str(row["chat_id"]),
                    language=row["language"] or "en",
                    currency=row["currency"] or "PLN",
                )
            )
        session.execute(text(
        "SELECT setval(pg_get_serial_sequence('entries','id'), "
        "COALESCE((SELECT MAX(id) FROM entries), 1))"
    ))
        session.commit()
        print("Committed.")
    sqlite_conn.close()
    print(f"Migration completed: {len(entries)} entries, {len(settings)} user settings")


if __name__ == "__main__":
    migrate()