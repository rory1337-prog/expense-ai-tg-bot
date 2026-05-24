# ===== IMPORTS =====
import logging
import sqlite3
from config import DB_FILE
from parser import detect_category

logger = logging.getLogger(__name__)

# ===== DATABASE CONNECTION =====
def get_connection():
    return sqlite3.connect(DB_FILE)

# ===== DATABASE INIT =====
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            chat_id TEXT PRIMARY KEY,
            language TEXT DEFAULT 'en',
            currency TEXT DEFAULT 'PLN'
        )
    """)

    conn.commit()
    conn.close()

# ===== SAVE OPERATIONS =====
def save_entry(entry, chat_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO entries (chat_id, name, amount, category, type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            chat_id,
            entry["name"],
            entry["amount"],
            entry["category"],
            entry["type"],
            entry["created_at"]
        ))

        conn.commit()
        conn.close()
        return True

    except Exception:
        logger.exception("Failed to save entry")
        return False
    
# ===== GET OPERATIONS =====
def get_user_entries(chat_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, category, type, created_at
        FROM entries
        WHERE chat_id = ?
        ORDER BY id DESC
    """, (chat_id,))

    rows = cursor.fetchall()
    conn.close()

    entries = []
    for row in rows:
        entries.append({
            "id": row[0],
            "name": row[1],
            "amount": row[2],
            "category": row[3],
            "type": row[4],
            "created_at": row[5]
        })

    return entries

# ===== DELETE OPERATIONS =====
def delete_last_entry(chat_id):
    entries = get_user_entries(chat_id)
    
    if not entries:
        return None
    
    last_entry = entries[0]
    entry_id = last_entry['id']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM entries
        WHERE id = ?
    ''', (entry_id,))
    conn.commit()
    conn.close()

    return last_entry


def delete_entry_by_number(chat_id, number):
    entries = get_user_entries(chat_id)
    expense_items = [item for item in entries if item['type'] == 'expense']

    if number < 1 or number > len(expense_items):
        return None
    
    entry_to_delete = expense_items[number - 1]
    entry_id = entry_to_delete['id']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM entries
        WHERE id = ?
    ''', (entry_id,))

    conn.commit()
    conn.close()
    

    return entry_to_delete

def delete_entry_by_id(chat_id, entry_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, category, type, created_at
        FROM entries
        WHERE chat_id = ? AND id = ?
    """, (chat_id, entry_id))

    row = cursor.fetchone()

    if not row:
        conn.close()
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

    conn.commit()
    conn.close()

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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE entries
        SET name = ?, amount = ?, category = ?
        WHERE id = ?
    ''', (name, amount, category, entry_id))

    conn.commit()
    conn.close()

    return {
        'name': name,
        'amount': amount,
        'category': category
    }

def update_entry_by_id(chat_id, entry_id, name, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE entries
        SET name = ?, amount = ?
        WHERE chat_id = ? AND id = ?
    """, (name, amount, chat_id, entry_id))

    updated = cursor.rowcount

    conn.commit()
    conn.close()

    return updated > 0


def get_user_settings(chat_id):
    conn = get_connection()
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
        conn.commit()
        conn.close()
        return {"language": "en", "currency": "PLN"}

    conn.close()
    return {"language": row[0], "currency": row[1]}


def set_user_language(chat_id, language):
    get_user_settings(chat_id)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE user_settings
        SET language = ?
        WHERE chat_id = ?
    """, (language, chat_id))

    conn.commit()
    conn.close()


def set_user_currency(chat_id, currency):
    get_user_settings(chat_id)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE user_settings
        SET currency = ?
        WHERE chat_id = ?
    """, (currency, chat_id))

    conn.commit()
    conn.close()


def ensure_user_settings(chat_id, language="en", currency="PLN"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO user_settings (chat_id, language, currency)
        VALUES (?, ?, ?)
        """,
        (chat_id, language, currency)
    )

    conn.commit()
    conn.close()

# ===== DATABASE STARTUP =====
init_db()