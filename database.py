# ===== IMPORTS =====
import logging
import sqlite3
from config import DB_FILE
from db.session import Base, engine
from services.expense_service import ExpenseService
from services.settings_service import SettingsService

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
        return ExpenseService.save_entry(entry, chat_id)

    except Exception:
        logger.exception("Failed to save entry")
        return False
    
# ===== GET OPERATIONS =====
def get_user_entries(chat_id):
    return ExpenseService.get_user_entries(chat_id)

# ===== DELETE OPERATIONS =====
def delete_entry_by_id(chat_id, entry_id):
    return ExpenseService.delete_entry_by_id(chat_id, entry_id)


def delete_entry_by_number(chat_id, number):
    return ExpenseService.delete_entry_by_number(chat_id, number)


# ===== UPDATE OPERATIONS =====
def update_entry_by_number(chat_id, number, name, amount):
    return ExpenseService.update_entry_by_number(chat_id, number, name, amount)

def update_entry_by_id(chat_id, entry_id, name, amount):
    return ExpenseService.update_entry_by_id(
        chat_id,
        entry_id,
        name,
        amount,
    )


def get_user_settings(chat_id):
    return SettingsService.get_user_settings(chat_id)


def set_user_language(chat_id, language):
    SettingsService.set_user_language(chat_id, language)



def set_user_currency(chat_id, currency):
    SettingsService.set_user_currency(chat_id, currency)


def ensure_user_settings(chat_id, language="en", currency="PLN"):
    SettingsService.ensure_user_settings(chat_id, language, currency)

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