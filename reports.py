# ===== IMPORTS =====
from datetime import datetime
from pathlib import Path
import sqlite3

from config import CURRENCY
from database import get_user_entries, get_connection

# ===== REPORTS =====
def build_report(chat_id):
    data = get_user_entries(chat_id)
    expense_items = [item for item in data if item["type"] == "expense"]
    total = sum(item["amount"] for item in expense_items)

    report = f'Total: {CURRENCY}{total:.2f}\n\n'

    for i, item in enumerate(expense_items, start=1):
        report += f'{i}. {item["name"]} ({CURRENCY}{item["amount"]}) [{item["category"]}]\n'

    return report

# ===== PERIOD REPORTS =====
def build_period_report(chat_id, period):
    conn = get_connection()
    cursor = conn.cursor()

    if period == "today":
        cursor.execute('''
            SELECT id, name, amount, category, created_at
            FROM entries
            WHERE chat_id = ?
                AND type = "expense"
                AND date(created_at) = date("now", "localtime")
            ORDER BY id DESC
        ''', (chat_id,))
        title = '📅 Today'

    elif period == "week":
        cursor.execute('''
            SELECT id, name, amount, category, created_at
            FROM entries
            WHERE chat_id = ?
                AND type = "expense"
                AND date(created_at) >= date("now", "localtime", "-6 days")
                AND date(created_at) <= date("now", "localtime")
            ORDER BY id DESC
        ''', (chat_id,))
        title = '📆 Last 7 days'

    elif period == "month":
        cursor.execute('''
            SELECT id, name, amount, category, created_at
            FROM entries
            WHERE chat_id = ?
                AND type = "expense"
                AND strftime("%Y-%m", created_at) = strftime("%Y-%m", "now", "localtime")
            ORDER BY id DESC
        ''', (chat_id,))
        title = '🗓 This month'

    else:
        conn.close()
        return 'Unknown period'
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"{title}\n\nNo expenses found"
    
    total = sum(row[2] for row in rows)

    text = f'{title}\n'
    text += f'Total: {CURRENCY} {total:.2f}\n\n'

    for i, row in enumerate(rows, start=1):
        _, name, amount, category, created_at = row
        text += f'{i}: {name} ({CURRENCY} {amount:.2f}) [{category}]\n'

    return text

# ===== BALANCE =====
def build_balance(chat_id):
    data = get_user_entries(chat_id)

    income_items = [item for item in data if item["type"] == "income"]
    expense_items = [item for item in data if item["type"] == "expense"]

    income_total = sum(item["amount"] for item in income_items)
    expense_total = sum(item["amount"] for item in expense_items)
    balance = income_total - expense_total

    return (
        f'Balance: {CURRENCY}{balance:.2f}\n\n'
        f'Income: {CURRENCY}{income_total:.2f}\n'
        f'Expenses: {CURRENCY}{expense_total:.2f}'
    )

# ===== ANALYTICS =====
def build_analytics(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # === TOTALS ===
    cursor.execute("""
        SELECT
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END),
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)
        FROM entries
        WHERE chat_id = ?
    """, (chat_id,))

    income_total, expense_total = cursor.fetchone()
    income_total = income_total or 0
    expense_total = expense_total or 0
    balance = income_total - expense_total

    # === TODAY ===
    today = datetime.now().date().isoformat()

    cursor.execute('''
        SELECT SUM(amount)
        FROM entries
        WHERE chat_id = ?
        AND type = 'expense'
        AND date(created_at) = ?
    ''', (chat_id, today))

    today_expense = cursor.fetchone()[0] or 0

    # === MONTHS ===
    month = datetime.now().strftime('%Y-%m')

    cursor.execute('''
        SELECT SUM(amount)
        FROM entries
        WHERE chat_id = ?
        AND type = 'expense'
        AND strftime('%Y-%m', created_at) = ?
    ''', (chat_id, month))

    month_expense = cursor.fetchone()[0] or 0

    # === TOP CATEGORIES ===
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM entries
        WHERE chat_id = ?
        AND type = 'expense'
        GROUP BY category
        ORDER BY total DESC
        LIMIT 3
    """, (chat_id,))

    categories = cursor.fetchall()

     # === LAST 5 EXPENSES ===
    cursor.execute("""
        SELECT name, amount
        FROM entries
        WHERE chat_id = ?
        AND type = 'expense'
        ORDER BY id DESC
        LIMIT 5
    """, (chat_id,))

    last_expenses = cursor.fetchall()

    conn.close()

    text = f"📊 Analytics\n\n"

    text += f"Balance: {CURRENCY} {balance:.2f}\n"
    text += f"Income: {CURRENCY} {income_total:.2f}\n"
    text += f"Expenses: {CURRENCY} {expense_total:.2f}\n\n"

    text += f"Today: {CURRENCY} {today_expense:.2f}\n"
    text += f"This month: {CURRENCY} {month_expense:.2f}\n\n"

    text += "Top categories:\n"
    if not categories:
        text += "No data\n"
    else:
        for cat, total in categories:
            text += f"- {cat}: {CURRENCY} {total:.2f}\n"

    text += "\nLast expenses:\n"
    if not last_expenses:
        text += "No expenses yet\n"
    else:
        for name, amount in last_expenses:
            text += f"- {name}: {CURRENCY} {amount:.2f}\n"

    return text

# ===== EXPORT =====
def export_data(chat_id):
    entries = get_user_entries(chat_id)

    if not entries:
        return None

    now = datetime.now().strftime("%Y-%m-%d")
    export_file = Path(__file__).with_name(f"expensesAI_export_{now}.txt")
    income = sum(item["amount"] for item in entries if item["type"] == "income")
    expense = sum(item["amount"] for item in entries if item["type"] == "expense")
    balance = income - expense

    lines = []
    lines.append("💸 ExpensesAI Export")
    lines.append(f"Date: {now}")
    lines.append("")
    lines.append(f"Balance: {CURRENCY}{balance:.2f}")
    lines.append(f"Income: {CURRENCY}{income:.2f}")
    lines.append(f"Expenses: {CURRENCY}{expense:.2f}")
    lines.append("")

    for i, item in enumerate(entries, start=1):
        lines.append(f"{i}. {item['created_at']}")
        lines.append(f"   Type: {item['type']}")
        lines.append(f"   Name: {item['name']}")
        lines.append(f"   Amount: {CURRENCY}{item['amount']}")
        lines.append(f"   Category: {item['category']}")
        lines.append("")

    with open(export_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return export_file

