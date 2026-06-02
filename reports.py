# ===== IMPORTS =====
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from database import get_user_entries, get_connection, get_user_settings
from locales import t
from locales.categories import localize_category


def get_locale_data(chat_id):
    settings = get_user_settings(chat_id)
    return settings["language"], settings["currency"]


# ===== REPORTS =====
def build_report(chat_id):
    lang, currency = get_locale_data(chat_id)

    data = get_user_entries(chat_id)
    expense_items = [item for item in data if item["type"] == "expense"]

    if not expense_items:
        return t("no_expenses", lang)

    total = sum(item["amount"] for item in expense_items)

    report = f'{t("total", lang)}: {total:.2f} {currency}\n\n'

    for i, item in enumerate(expense_items, start=1):
        report += (
            f'{i}. {item["name"]} '
            f'({item["amount"]:.2f} {currency}) '
            f'[{localize_category(item["category"], lang)}]\n'
        )

    return report


# ===== PERIOD REPORTS =====
def build_period_report(chat_id, period):
    lang, currency = get_locale_data(chat_id)

    conn = get_connection()
    cursor = conn.cursor()

    if period == "today":
        title = f"📅 {t('today', lang)}"
        query = '''
            SELECT id, name, amount, category, created_at
            FROM entries
            WHERE chat_id = ?
                AND type = "expense"
                AND date(created_at) = date("now", "localtime")
            ORDER BY id DESC
        '''

    elif period == "week":
        title = f"📆 {t('week', lang)}"
        query = '''
            SELECT id, name, amount, category, created_at
            FROM entries
            WHERE chat_id = ?
                AND type = "expense"
                AND date(created_at) >= date("now", "localtime", "-6 days")
                AND date(created_at) <= date("now", "localtime")
            ORDER BY id DESC
        '''

    elif period == "month":
        title = f"🗓 {t('month', lang)}"
        query = '''
            SELECT id, name, amount, category, created_at
            FROM entries
            WHERE chat_id = ?
                AND type = "expense"
                AND strftime("%Y-%m", created_at) = strftime("%Y-%m", "now", "localtime")
            ORDER BY id DESC
        '''

    else:
        conn.close()
        return t("unknown_period", lang)

    cursor.execute(query, (chat_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"{title}\n\n{t('no_expenses', lang)}"

    total = sum(row[2] for row in rows)

    text = f"{title}\n"
    text += f"{t('total', lang)}: {total:.2f} {currency}\n\n"

    for i, row in enumerate(rows, start=1):
        _, name, amount, category, created_at = row
        text += f"{i}. {name} ({amount:.2f} {currency}) [{localize_category(category, lang)}]\n"

    return text


# ===== BALANCE =====
def build_balance(chat_id):
    lang, currency = get_locale_data(chat_id)

    data = get_user_entries(chat_id)

    income_items = [item for item in data if item["type"] == "income"]
    expense_items = [item for item in data if item["type"] == "expense"]

    income_total = sum(item["amount"] for item in income_items)
    expense_total = sum(item["amount"] for item in expense_items)
    balance = income_total - expense_total

    return (
        f"{t('balance', lang)}: {balance:.2f} {currency}\n\n"
        f"{t('income', lang)}: {income_total:.2f} {currency}\n"
        f"{t('expenses', lang)}: {expense_total:.2f} {currency}"
    )


# ===== ANALYTICS =====
def build_analytics(chat_id):
    lang, currency = get_locale_data(chat_id)

    conn = get_connection()
    cursor = conn.cursor()

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

    today = datetime.now().date().isoformat()

    cursor.execute('''
        SELECT SUM(amount)
        FROM entries
        WHERE chat_id = ?
        AND type = 'expense'
        AND date(created_at) = ?
    ''', (chat_id, today))

    today_expense = cursor.fetchone()[0] or 0

    month = datetime.now().strftime("%Y-%m")

    cursor.execute('''
        SELECT SUM(amount)
        FROM entries
        WHERE chat_id = ?
        AND type = 'expense'
        AND strftime('%Y-%m', created_at) = ?
    ''', (chat_id, month))

    month_expense = cursor.fetchone()[0] or 0

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

    text = f"📊 {t('analytics', lang)}\n\n"

    text += f"{t('balance', lang)}: {balance:.2f} {currency}\n"
    text += f"{t('income', lang)}: {income_total:.2f} {currency}\n"
    text += f"{t('expenses', lang)}: {expense_total:.2f} {currency}\n\n"

    text += f"{t('today', lang)}: {today_expense:.2f} {currency}\n"
    text += f"{t('month', lang)}: {month_expense:.2f} {currency}\n\n"

    text += f"{t('top_categories', lang)}:\n"

    if not categories:
        text += f"{t('no_data', lang)}\n"
    else:
        for cat, total in categories:
            text += f"- {localize_category(cat, lang)}: {total:.2f} {currency}\n"

    text += f"\n{t('last_expenses', lang)}:\n"

    if not last_expenses:
        text += f"{t('no_expenses_yet', lang)}\n"
    else:
        for name, amount in last_expenses:
            text += f"- {name}: {amount:.2f} {currency}\n"

    return text


# ===== EXPORT =====
def export_data(chat_id):
    lang, currency = get_locale_data(chat_id)

    entries = get_user_entries(chat_id)

    if not entries:
        return None

    now = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid4().hex(:8)

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    export_file = export_dir / f"expensesAI_export_{chat_id}_{timestamp}_{unique_id}.txt"

    income = sum(item["amount"] for item in entries if item["type"] == "income")
    expense = sum(item["amount"] for item in entries if item["type"] == "expense")
    balance = income - expense

    lines = []
    lines.append("💸 ExpensesAI Export")
    lines.append(f"{t('date', lang)}: {now}")
    lines.append("")
    lines.append(f"{t('balance', lang)}: {balance:.2f} {currency}")
    lines.append(f"{t('income', lang)}: {income:.2f} {currency}")
    lines.append(f"{t('expenses', lang)}: {expense:.2f} {currency}")
    lines.append("")

    for i, item in enumerate(entries, start=1):
        lines.append(f"{i}. {item['created_at']}")
        lines.append(f"   {t('type', lang)}: {item['type']}")
        lines.append(f"   {t('name', lang)}: {item['name']}")
        lines.append(f"   {t('amount', lang)}: {item['amount']:.2f} {currency}")
        lines.append(f"   {t('category', lang)}: {localize_category(item['category'], lang)}")
        lines.append("")

    with open(export_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return export_file