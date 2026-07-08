# ===== IMPORTS =====
import logging
import sqlite3
from sqlalchemy import select, delete
from config import DB_FILE
from parser import detect_category
from db.session import Base, engine, SessionLocal
from db.models import Entry
from db import models

logger = logging.getLogger(__name__)

# ===== DATABASE CONNECTION =====
def get_connection():
    return sqlite3.connect(DB_FILE)

# ===== DATABASE INIT =====
def init_db():
    Base.metadata.create_all(bind=engine)

# ===== SAVE OPERATIONS =====
def save_entry(entry, chat_id):
    try:
        with SessionLocal() as session:
            db_entry = Entry(
                chat_id=str(chat_id),
                name=entry["name"],
                amount=entry["amount"],
                category=entry["category"],
                type=entry["type"],
                created_at=entry["created_at"],
            )

            session.add(db_entry)
            session.commit()

        return True
    
    except Exception:
        logger.exception("Failed to save entry")
        return False
    
# ===== GET OPERATIONS =====
def get_user_entries(chat_id):
    with SessionLocal() as session:
        stmt = (
            select(Entry)
            .where(Entry.chat_id == str(chat_id))
            .order_by(Entry.id.desc())
        )
        rows = session.execute(stmt).scalars().all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "amount": row.amount,
            "category": row.category,
            "type": row.type,
            "created_at": row.created_at,
        }
        for row in rows
    ]

# ===== DELETE OPERATIONS =====
def delete_entry_by_ia(chat_id, entry_id):
    with SessionLocal() as session:
        stmt = select(Entry).where(
            Entry.chat_id == str(chat_id),
            Entry.id == entry_id,
        )

        entry = session.execute(stmt).scalar_one_or_none()

        if not entry:
            return None
        
        deleted_entry = {
            "id": entry.id,
            "name": entry.name,
            "amount": entry.amount,
            "category": entry.category,
            "type": entry.type,
            "created_at": entry.created_at,
        }

        session.delete(entry)
        session.commit()
    return deleted_entry


def delete_entry_by_number(chat_id, number):
    entries = get_user_entries(chat_id)
    expense_items = [item for item in entries if item['type'] == 'expense']

    if number < 1 or number > len(expense_items):
        return None
    
    entry_to_delete = expense_items[number - 1]
    entry_id = entry_to_delete['id']

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM entries
            WHERE id = ?
        ''', (entry_id,))

    return entry_to_delete

def delete_entry_by_id(chat_id, entry_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, amount, category, type, created_at
            FROM entries
            WHERE chat_id = ? AND id = ?
        """, (chat_id, entry_id))

        row = cursor.fetchone()

        if not row:
            return None

        deleted_entry = {
            "id": row[0],
            "name": row[1],
            "amount": row[2],
            "category": row[3],
            "type": row[4],
            "created_at": row[5]
        }

        cursor.execute("""
            DELETE FROM entries
            WHERE chat_id = ? AND id = ?
        """, (chat_id, entry_id))

    return deleted_entry

# ===== UPDATE OPERATIONS =====
def update_entry_by_number(chat_id, number, name, amount):
    entries = get_user_entries(chat_id)
    expense_items = [item for item in entries if item['type'] == 'expense']

    if number < 1 or number > len(expense_items):
        return None
    
    entry = expense_items[number - 1]
    entry_id = entry['id']

    category = detect_category(name)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE entries
            SET name = ?, amount = ?, category = ?
            WHERE id = ?
        ''', (name, amount, category, entry_id))

    return {
        'name': name,
        'amount': amount,
        'category': category
    }

def update_entry_by_id(chat_id, entry_id, name, amount):
    category = detect_category(name)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE entries
            SET name = ?, amount = ?, category = ?
            WHERE chat_id = ? AND id = ?
        """, (name, amount, category, chat_id, entry_id))

        updated = cursor.rowcount
        
    return updated > 0


def get_user_settings(chat_id):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT language, currency
            FROM user_settings
            WHERE chat_id = ?
        """, (chat_id,))

        row = cursor.fetchone()

        if not row:
            cursor.execute("""
                INSERT INTO user_settings (chat_id, language, currency)
                VALUES (?, ?, ?)
            """, (chat_id, "en", "PLN"))
            
            return {"language": "en", "currency": "PLN"}

    return {"language": row[0], "currency": row[1]}


def set_user_language(chat_id, language):
    get_user_settings(chat_id)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_settings
            SET language = ?
            WHERE chat_id = ?
        """, (language, chat_id))


def set_user_currency(chat_id, currency):
    get_user_settings(chat_id)

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_settings
            SET currency = ?
            WHERE chat_id = ?
        """, (currency, chat_id))


def ensure_user_settings(chat_id, language="en", currency="PLN"):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO user_settings (chat_id, language, currency)
            VALUES (?, ?, ?)
            """,
            (chat_id, language, currency)
        )

def get_total_spending(chat_id, period):
    with get_connection() as conn:
        cursor = conn.cursor()

        if period == "week":
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-7 days')
            """, (chat_id,))

        elif period == "month":
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-30 days')
            """, (chat_id,))

        elif period == "today":
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND date(created_at) = date('now')
            """, (chat_id,))

        else:
            
            return 0
        result = cursor.fetchone()[0]
        
        return result or 0
    
def get_category_spending(chat_id, category, period):
    with get_connection() as conn:
        cursor = conn.cursor()

        if period == "week":
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND category = ?
                AND datetime(created_at) >= datetime('now', '-7 days')
            """, (chat_id, category))

        elif period == 'month':
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND category = ?
                AND datetime(created_at) >= datetime('now', '-30 days')
            """, (chat_id, category))

        elif period == 'today':
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND category = ?
                AND date(created_at) = date('now')
            """, (chat_id, category))

        else:
            return 0
        
        result = cursor.fetchone()[0]
        return result or 0
        
    
def get_top_category(chat_id, period):
    with get_connection() as conn:
        cursor = conn.cursor()

        if period == "week":
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-7 days')
                GROUP BY category
                ORDER BY total DESC
                LIMIT 1
            """, (chat_id,))

        elif period == "month":
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-30 days')
                GROUP BY category
                ORDER BY total DESC
                LIMIT 1
            """, (chat_id,))

        elif period == "today":
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND date(created_at) = date('now')
                GROUP BY category
                ORDER BY total DESC
                LIMIT 1
            """, (chat_id,))

        else:
            
            return None

        result = cursor.fetchone()
    

    if not result:
        return None

    return {
        "category": result[0],
        "total": result[1]
    }

def get_biggest_expenses(chat_id, period, limit=5):
    with get_connection() as conn:
        cursor = conn.cursor()

        if period == "week":
            cursor.execute("""
                SELECT name, amount, category, created_at
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-7 days')
                ORDER BY amount DESC
                LIMIT ?
            """, (chat_id, limit))

        elif period == "month":
            cursor.execute("""
                SELECT name, amount, category, created_at
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-30 days')
                ORDER BY amount DESC
                LIMIT ?
            """, (chat_id, limit))

        elif period == "today":
            cursor.execute("""
                SELECT name, amount, category, created_at
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND date(created_at) = date('now')
                ORDER BY amount DESC
                LIMIT ?
            """, (chat_id, limit))

        else:
            return []

        rows = cursor.fetchall()

    return [
        {
            "name": row[0],
            "amount": row[1],
            "category": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]

def get_avarage_daily_spending(chat_id, period):
    with get_connection() as conn:
        cursor = conn.cursor()

        if period == "week":
            days = 7
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-7 days')
            """, (chat_id,))

        elif period == "month":
            days = 30
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND datetime(created_at) >= datetime('now', '-30 days')
            """, (chat_id,))

        elif period == "today":
            days = 1
            cursor.execute("""
                SELECT SUM(amount)
                FROM entries
                WHERE chat_id = ?
                AND type = 'expense'
                AND date(created_at) = date('now')
            """, (chat_id,))
        
        else:
            return 0
        
        result = cursor.fetchone()[0]
        total = result or 0
        
        return total / days