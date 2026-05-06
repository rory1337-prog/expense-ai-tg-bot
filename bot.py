# ===== IMPORTS =====
import requests
import os
import json
import time
import base64
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# ===== CONFIG =====
load_dotenv(dotenv_path=Path(__file__).with_name('.env'), override=True)
db_file = Path(__file__).with_name("expenses.db")
update_file = Path(__file__).with_name('update.txt')

bot_token = os.getenv("BOTTOKEN", "").strip()

telegram_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
telegram_document_url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
currency = 'PLN'

# ===== CATEGORY RULES =====
CATEGORY_KEYWORDS = {
    "food": [
        "coffee", "pizza", "burger", "sushi", "kfc", "mcdonalds",
        "restaurant", "cafe", "bar", "doner", "shawarma",
        "meal", "lunch", "dinner"
    ],

    "groceries": [
        "lidl", "kaufland", "biedronka", "zabka", "auchan",
        "carrefour", "tesco", "aldi", "grocery", "supermarket"
    ],

    "transport": [
        "taxi", "uber", "bolt", "bus", "train", "tram",
        "metro", "fuel", "gasoline", "petrol", "parking", "ticket"
    ],

    "shopping": [
        "spodnie", "shoes", "shirt", "jacket", "clothes",
        "zara", "hm", "h&m", "reserved", "allegro", "amazon",
        "nike", "adidas", "cosmetics"
    ],

    "health": [
        "pharmacy", "apteka", "doctor", "dentist",
        "medicine", "hospital", "clinic", "therapy", "vitamins"
    ],

    "entertainment": [
        "cinema", "movie", "netflix", "spotify",
        "steam", "game", "psn", "xbox", "concert"
    ],

    "bills": [
        "rent", "internet", "wifi", "phone",
        "electricity", "water", "gas", "utility",
        "utilities", "subscription"
    ],

    "services": [
        "barber", "haircut", "nails", "cleaning",
        "repair", "service", "mechanic", "washing", "laundry"
    ],

    "education": [
        "course", "udemy", "book", "lesson",
        "study", "education", "training", "school"
    ]
}

# ===== TEXT PARSING =====
def parse_expense(text):
    try:
        parts = text.split()
        name = parts[0]
        amount = float(parts[1])
        category =  detect_category(name)
        return {'name': name, 'amount': amount, 'category': category, 'type': 'expense', 'created_at': datetime.now().replace(microsecond=0).isoformat()}
    
    except Exception:
        return None
    
def detect_category(name):
    name = name.lower().strip().replace(',', '').replace('.', '')

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name:
                return category

    return "other"
    
# ===== AI RECEIPT PARSING =====
def ai_parse_photo(image_path):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("OPENAI_API_KEY not found")
        return None

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract one expense from this receipt image. "
                            "Return only the structured result."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "expense_receipt",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "amount": {"type": "number"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "food",
                                "groceries",
                                "transport",
                                "shopping",
                                "health",
                                "entertainment",
                                "bills",
                                "services",
                                "education",
                                "other"
                            ],
                        },
                    },
                    "required": ["name", "amount", "category"],
                },
                "strict": True,
            }
        },
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        print("OPENAI ERROR:", response.status_code, response.text)
        return None

    data = response.json()

    try:
        output_items = data.get("output", [])
        text_output = None

        for item in output_items:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text_output = content.get("text")
                    break
            if text_output:
                break

        if not text_output:
            print("No output_text in OpenAI response")
            return None

        expense = json.loads(text_output)

        expense["name"] = str(expense["name"]).strip()
        expense["amount"] = float(expense["amount"])
        expense["category"] = detect_category(expense["name"])

        allowed = {
            "food",
            "groceries",
            "transport",
            "shopping",
            "health",
            "entertainment",
            "bills",
            "services",
            "education",
            "other"
        }
        if expense["category"] not in allowed:
            expense["category"] = "other"
        expense['type'] = 'expense'
        expense['created_at'] = datetime.now().replace(microsecond=0).isoformat()

        return expense

    except Exception as e:
        print("AI PARSE ERROR:", e)
        return None

# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
init_db()

def save_expense(expense, chat_id):
    try:
        init_db()

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO entries (chat_id, name, amount, category, type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            chat_id,
            expense["name"],
            expense["amount"],
            expense["category"],
            expense["type"],
            expense["created_at"]
        ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print("SAVE EXPENSE ERROR:", e)
        return False

def get_user_entries(chat_id):
    conn = sqlite3.connect(db_file)
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

# ===== ENTRY MANAGEMENT =====
def delete_last_entry(chat_id):
    entries = get_user_entries(chat_id)
    
    if not entries:
        return None
    
    last_entry = entries[0]
    entry_id = last_entry['id']

    conn = sqlite3.connect(db_file)
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

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM entries
        WHERE id = ?
    ''', (entry_id,))

    conn.commit()
    conn.close()
    

    return entry_to_delete

def update_entry_by_number(chat_id, number, name, amount):
    entries = get_user_entries(chat_id)
    expense_items = [item for item in entries if item['type'] == 'expense']

    if number < 1 or number > len(expense_items):
        return None
    
    entry = expense_items[number - 1]
    entry_id = entry['id']

    category = detect_category(name)

    conn = sqlite3.connect(db_file)
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

# ===== REPORTS =====
def build_report(chat_id):
    data = get_user_entries(chat_id)
    expense_items = [item for item in data if item["type"] == "expense"]
    total = sum(item["amount"] for item in expense_items)

    report = f'Total: {currency}{total:.2f}\n\n'

    for i, item in enumerate(expense_items, start=1):
        report += f'{i}. {item["name"]} ({currency}{item["amount"]}) [{item["category"]}]\n'

    return report

def build_period_report(chat_id, period):
    conn = sqlite3.connect(db_file)
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
    text += f'Total: {currency} {total:.2f}\n\n'

    for i, row in enumerate(rows, start=1):
        _, name, amount, category, created_at = row
        text += f'{i}: {name} ({currency} {amount:.2f}) [{category}]\n'

    return text

def build_balance(chat_id):
    data = get_user_entries(chat_id)

    income_items = [item for item in data if item["type"] == "income"]
    expense_items = [item for item in data if item["type"] == "expense"]

    income_total = sum(item["amount"] for item in income_items)
    expense_total = sum(item["amount"] for item in expense_items)
    balance = income_total - expense_total

    return (
        f'Balance: {currency}{balance:.2f}\n\n'
        f'Income: {currency}{income_total:.2f}\n'
        f'Expenses: {currency}{expense_total:.2f}'
    )

def build_analytics(chat_id):
    conn = sqlite3.connect(db_file)
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

    text += f"Balance: {currency} {balance:.2f}\n"
    text += f"Income: {currency} {income_total:.2f}\n"
    text += f"Expenses: {currency} {expense_total:.2f}\n\n"

    text += f"Today: {currency} {today_expense:.2f}\n"
    text += f"This month: {currency} {month_expense:.2f}\n\n"

    text += "Top categories:\n"
    if not categories:
        text += "No data\n"
    else:
        for cat, total in categories:
            text += f"- {cat}: {currency} {total:.2f}\n"

    text += "\nLast expenses:\n"
    if not last_expenses:
        text += "No expenses yet\n"
    else:
        for name, amount in last_expenses:
            text += f"- {name}: {currency} {amount:.2f}\n"

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
    lines.append(f"Balance: {currency}{balance:.2f}")
    lines.append(f"Income: {currency}{income:.2f}")
    lines.append(f"Expenses: {currency}{expense:.2f}")
    lines.append("")

    for i, item in enumerate(entries, start=1):
        lines.append(f"{i}. {item['created_at']}")
        lines.append(f"   Type: {item['type']}")
        lines.append(f"   Name: {item['name']}")
        lines.append(f"   Amount: {currency}{item['amount']}")
        lines.append(f"   Category: {item['category']}")
        lines.append("")

    with open(export_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return export_file

# ===== TELEGRAM UPDATES =====
offset = None
if update_file.exists():
    with open(update_file, 'r') as f:
        last_update_id = int(f.read())
        offset = last_update_id + 1
else:
    last_update_id = None

def get_updates(offset):
    try:
        url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
        params = {}
        if offset is not None:
            params["offset"] = offset

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print("GET UPDATES ERROR:", e)
        return {"result": []}

# ===== MAIN LOOP =====
try:
    while True:
        data = get_updates(offset)

        if not data["result"]:
            time.sleep(0.5)
            continue

        for update in data["result"]:
            update_id = update["update_id"]
            message = update.get("message")

            if not message:
                with open(update_file, 'w') as f:
                    f.write(str(update_id))
                offset = update_id + 1
                continue

            chat_id = str(message['chat']['id'])

            # ===== PHOTO MESSAGE =====
            if 'photo' in message:
                try:
                    photos = message['photo']
                    largest_photo = photos[-1]
                    file_id = largest_photo['file_id']

                    photo_url = f'https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}'
                    response = requests.get(photo_url, timeout=20)
                    response.raise_for_status()
                    file_data = response.json()

                    file_path = file_data["result"]["file_path"]

                    download_url = f'https://api.telegram.org/file/bot{bot_token}/{file_path}'
                    file_response = requests.get(download_url, timeout=30)
                    file_response.raise_for_status()

                    receipt_file = Path(__file__).with_name(f"receipt_{update_id}.jpg")
                    with open(receipt_file, 'wb') as f:
                        f.write(file_response.content)

                    expense = ai_parse_photo(receipt_file)
                    receipt_file.unlink(missing_ok=True)

                    if expense is not None:
                        saved = save_expense(expense, chat_id)

                        if saved:
                            payload = {
                                'chat_id': chat_id,
                                'text': f'Saved: {expense["name"]} ({currency}{expense["amount"]:.2f}) [{expense["category"]}]'
                            }
                        else:
                            payload = {
                                'chat_id': chat_id,
                                'text': 'Error: could not save parsed receipt'
                            }
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': 'Could not read receipt'
                        }

                except Exception as e:
                    print("PHOTO PROCESSING ERROR:", e)
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Error: could not process photo'
                    }

                requests.post(telegram_url, data=payload, timeout=10)

                with open(update_file, 'w') as f:
                    f.write(str(update_id))
                offset = update_id + 1
                continue
            
            # ===== NON-TEXT MESSAGE =====
            elif 'text' not in message:
                payload = {
                    'chat_id': chat_id,
                    'text': 'Only text and photo messages are supported'
                }
                requests.post(telegram_url, data=payload, timeout=10)

                with open(update_file, 'w') as f:
                    f.write(str(update_id))
                offset = update_id + 1
                continue
            
            # ===== TEXT MESSAGE =====
            text = message['text']
            
            # ===== COMMAND: START =====
            if text == '/start':
                payload = {
                    'chat_id': chat_id,
                    'text': (
                        '💸 ExpensesAI\n\n'
                        'Track your money simply:\n\n'
                        
                        '📥 Add expense:\n'
                        'coffee 15\n\n'
                        
                        '💰 Add income:\n'
                        '/income salary 3000\n\n'
                        
                        '📊 Commands:\n'
                        '/report — expenses list\n'
                        '/today — today expenses\n'
                        '/week — weekly expenses\n'
                        '/month — monthly expenses\n'
                        '/balance — income vs expenses\n'
                        '/analytics — money overview\n'
                        '/export — download your data\n'
                        '/help — show commands\n\n'
                        
                        '📷 You can also send a receipt photo'
                    )
                }
                
            # ===== COMMAND: HELP =====
            elif text == '/help':
                payload = {
                    'chat_id': chat_id,
                    'text': (
                        '📘 ExpensesAI — Help\n\n'
                        
                        '💸 Track your money easily:\n\n'
                        
                        '📥 Add expense:\n'
                        'coffee 15\n\n'
                        
                        '💰 Add income:\n'
                        '/income salary 3000\n\n'
                        
                        '📊 Commands:\n'
                        '/report — show all expenses\n'
                        '/balance — income vs expenses\n'
                        '/analytics — show analytics\n'
                        '/delete last — delete last entry (income or expense)\n'
                        '/delete 1 — delete entry by number\n'
                        '/edit 1 coffee 25 — edit expense by number\n'
                        '/today — today expenses\n'
                        '/week — last 7 days expenses\n'
                        '/month — current month expenses\n'
                        '/export — download your data\n'
                        '/income — add income\n'
                        '/start — restart bot\n\n'
                        
                        '📷 Receipt parsing:\n'
                        'Send a photo → bot will extract expense automatically\n\n'
                        
                        '⚡ Tips:\n'
                        '- Use simple names (coffee, uber, lidl)\n'
                        '- Amount must be a number\n'
                        '- Categories are auto-detected\n'
                    )
                }
                
            # ===== COMMAND: INCOME =====       
            elif text.startswith('/income'):

                try:
                    parts = text.split()
                    name = parts[1]
                    amount = float(parts[2])
                    income = {
                        'name': name,
                        'amount': amount,
                        'category': 'income',
                        'type': 'income',
                        'created_at': datetime.now().replace(microsecond=0).isoformat()
                    }
                    saved = save_expense(income, chat_id)
                    if saved:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Saved income: {name} ({currency}{amount})'
                        }

                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Error: could not save income'
                        }

                except Exception:
                    payload = {
                        'chat_id': chat_id,
                        'text': f'Incorrect format. Use: /income salary 3000'
                    }

            # ===== COMMAND: DELETE LAST =====
            elif text == '/delete last':
                deleted = delete_last_entry(chat_id)

                if deleted is None:
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Nothing to delete'
                    }
                else:
                    payload = {
                        'chat_id': chat_id,
                        'text': f'Deleted: {deleted["name"]} ({currency}{deleted["amount"]}) [{deleted["category"]}]'
                    }
            
            # ===== COMMAND: DELETE BY NUMBER =====
            elif text.startswith('/delete '):
                try:
                    parts = text.split()
                    number = int(parts[1])

                    deleted = delete_entry_by_number(chat_id, number)

                    if deleted is None:
                        payload = {
                            'chat_id': chat_id,
                            'text': 'Invalid entry number'
                        }
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Deleted: {deleted["name"]} ({currency}{deleted["amount"]}) [{deleted["category"]}]'
                        }
                
                except Exception:
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Use: /delete 1'
                    }
            
            # ===== COMMAND: EDIT =====
            elif text.startswith('/edit '):
                try:
                    parts = text.split()
                    number = int(parts[1])
                    name = parts[2]
                    amount = float(parts[3])

                    updated = update_entry_by_number(chat_id, number, name, amount)

                    if updated is None:
                        payload = {
                            'chat_id': chat_id,
                            'text': 'Invalid entry number'
                        }
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Updated: {updated["name"]} ({currency}{updated["amount"]}) [{updated["category"]}]'
                        }
                except Exception:
                    payload = {
                        'chat_id': chat_id,
                        'text': f'Use: /edit 1 coffee 25'
                    }
                    
            # ===== COMMAND: EXPORT =====        
            elif text == '/export':
                export_file = export_data(chat_id)

                if export_file is None:
                    payload = {
                        'chat_id': chat_id,
                        'text': 'No data to export'
                    }
                    requests.post(telegram_url, data=payload, timeout=10)
                else:
                    with open(export_file, 'rb') as f:
                        requests.post(
                            telegram_document_url,
                            data={'chat_id': chat_id},
                            files={'document': f},
                            timeout=20
                        )
                    export_file.unlink(missing_ok=True)
                    with open(update_file, 'w') as f:
                        f.write(str(update_id))
                    offset = update_id + 1
                    continue
                
            # ===== COMMAND: ANALYTICS =====    
            elif text == '/analytics':
                payload = {
                    'chat_id': chat_id,
                    'text': build_analytics(chat_id)
                }
                
            # ===== COMMAND: TODAY =====
            elif text == '/today':
                payload = {
                    'chat_id': chat_id,
                    'text': build_period_report(chat_id, 'today')
                }
            
            # ===== COMMAND: WEEK =====
            elif text == '/week':
                payload = {
                    'chat_id': chat_id,
                    'text': build_period_report(chat_id, 'week')
                }

            # ===== COMMAND: MONTH =====
            elif text == "/month":
                payload = {
                    'chat_id': chat_id,
                    'text': build_period_report(chat_id, 'month')
                } 

            # ===== COMMAND: REPORT =====    
            elif text == '/report':
                payload = {
                    'chat_id': chat_id,
                    'text': build_report(chat_id)
                }
                
            # ===== COMMAND: BALANCE =====    
            elif text == '/balance':
                payload = {
                    'chat_id': chat_id,
                    'text': build_balance(chat_id)
                }
                
            # ===== DEFAULT: PARSE EXPENSE TEXT =====    
            else:
                expense = parse_expense(text)
                
                if expense is not None:
                    saved = save_expense(expense, chat_id)
                    
                    if saved:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Saved: {expense["name"]} ({currency}{expense["amount"]}) [{expense["category"]}]'
                        }
                    
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': 'Error: could not save expense'
                        }
                    
                else:
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Incorrect format. Use: coffee 15'
                    }

            requests.post(telegram_url, data=payload, timeout=10)

            with open(update_file, 'w') as f:
                f.write(str(update_id))
            offset = update_id + 1

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Bot Stopped")






    




    
