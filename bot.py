# ===== IMPORTS =====
import time
import logging

from telegram_api import (
    send_message,
    send_document,
    get_updates,
    download_photo
)

from config import UPDATE_FILE, CURRENCY

from database import (
    save_entry,
    delete_last_entry,
    delete_entry_by_number,
    update_entry_by_number
)

from parser import parse_expense, parse_income

from ai import ai_parse_photo

from reports import (
    build_report,
    build_period_report,
    build_balance,
    build_analytics,
    export_data
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ===== COMMAND: START =====
def handle_start(chat_id):
    return {
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
            
            '📷 You can also send a receipt photo\n\n'

            '🧪 ExpensesAI is currently in beta.\n'
            'Feedback helps improve the bot:\n'
            '@grindbtco'
        )
    }

# ===== COMMAND: HELP =====
def handle_help(chat_id):
    return {
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

# ===== COMMAND: REPORT =====
def handle_report(chat_id):
    return {
        'chat_id': chat_id,
        'text': build_report(chat_id)
    }

# ===== COMMAND: BALANCE =====
def handle_balance(chat_id):
    return {
        'chat_id': chat_id,
        'text': build_balance(chat_id)
    }

# ===== COMMAND: ANALYTICS =====
def handle_analytics(chat_id):
    return {
        'chat_id': chat_id,
        'text': build_analytics(chat_id)
    }

# ===== COMMAND: DAY =====
def handle_today(chat_id):
    return {
        'chat_id': chat_id,
        'text': build_period_report(chat_id, 'today')
    }

# ===== COMMAND: WEEK =====
def handle_week(chat_id):
    return {
        'chat_id': chat_id,
        'text': build_period_report(chat_id, 'week')
    }

# ===== COMMAND: MONTH =====
def handle_month(chat_id):
    return {
        'chat_id': chat_id,
        'text': build_period_report(chat_id, 'month')
    }

# ===== COMMAND: INCOME ===== 
def handle_income(chat_id, text):
    income = parse_income(text)

    if income is None:
        return {
            'chat_id': chat_id,
            'text': 'Incorrect format. Use: /income salary 3000'
        }
    
    saved = save_entry(income, chat_id)

    if saved:
        return {
            'chat_id': chat_id,
            'text': f'Saved income: {income["name"]} ({CURRENCY}{income["amount"]})'
        }
    
    return {
        'chat_id': chat_id,
        'text': 'Error: could not save income'
    }

# ===== COMMAND: DELETE LAST =====
def handle_delete_last(chat_id):
    deleted = delete_last_entry(chat_id)

    if deleted is None:
        return {
            'chat_id': chat_id,
            'text': 'Nothing to delete'
        }

    return {
        'chat_id': chat_id,
        'text': f'Deleted: {deleted["name"]} ({CURRENCY}{deleted["amount"]}) [{deleted["category"]}]'
    }

def handle_delete_by_number(chat_id, text):
    try:
        parts = text.split()
        number = int(parts[1])

        deleted = delete_entry_by_number(chat_id, number)

        if deleted is None:
            return {
                'chat_id': chat_id,
                'text': 'Invalid entry number'
            }

        return {
            'chat_id': chat_id,
            'text': f'Deleted: {deleted["name"]} ({CURRENCY}{deleted["amount"]}) [{deleted["category"]}]'
        }

    except (ValueError, IndexError):
        return {
            'chat_id': chat_id,
            'text': 'Use: /delete 1'
        }
    
# ===== COMMAND: EDIT =====
def handle_edit(chat_id, text):
    try:
        parts = text.split()
        
        if len(parts) < 4:
            raise ValueError
        
        number = int(parts[1])
        amount = float(parts[-1])
        name = ' '.join(parts[2:-1]).strip()

        if amount <= 0 or not name:
            raise ValueError

        updated = update_entry_by_number(chat_id, number, name, amount)

        if updated is None:
            return {
                'chat_id': chat_id,
                'text': 'Invalid entry number'
            }

        return {
            'chat_id': chat_id,
            'text': f'Updated: {updated["name"]} ({CURRENCY}{updated["amount"]}) [{updated["category"]}]'
        }

    except (ValueError, IndexError):
        return {
            'chat_id': chat_id,
            'text': 'Use: /edit 1 coffee 25'
        }

# ===== DEFAULT: PARSE EXPENSE TEXT =====
def handle_expense_text(chat_id, text):
    expense = parse_expense(text)

    if expense is None:
        return {
            'chat_id': chat_id,
            'text': 'Incorrect format. Use: coffee 15'
        }

    saved = save_entry(expense, chat_id)

    if saved:
        return {
            'chat_id': chat_id,
            'text': f'Saved: {expense["name"]} ({CURRENCY}{expense["amount"]}) [{expense["category"]}]'
        }

    return {
        'chat_id': chat_id,
        'text': 'Error: could not save expense'
    }

# ===== COMMAND: EXPORT =====
def handle_export(chat_id):
    export_file = export_data(chat_id)

    if export_file is None:
        send_message(chat_id, 'No data to export')
        return None
    
    send_document(chat_id, export_file)
    export_file.unlink(missing_ok=True)
    return None

# ===== COMMAND HANDLERS =====
COMMAND_HANDLERS = {
    '/start': handle_start,
    '/help': handle_help,
    '/report': handle_report,
    '/balance': handle_balance,
    '/analytics': handle_analytics,
    '/today': handle_today,
    '/week': handle_week,
    '/month': handle_month,
    '/delete last': handle_delete_last,
}
# ===== TELEGRAM UPDATES =====
offset = None
if UPDATE_FILE.exists():
    with open(UPDATE_FILE, 'r') as f:
        last_update_id = int(f.read())
        offset = last_update_id + 1
else:
    last_update_id = None

# ===== MAIN LOOP =====
try:
    while True:
        data = get_updates(offset)

        if not data["result"]:
            time.sleep(0.1)
            continue

        for update in data["result"]:
            update_id = update["update_id"]
            message = update.get("message")

            if not message:
                with open(UPDATE_FILE, 'w') as f:
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

                    receipt_file = download_photo(file_id, update_id)

                    if receipt_file is None:
                        raise Exception("Could not download photo")

                    expense = ai_parse_photo(receipt_file)
                    receipt_file.unlink(missing_ok=True)

                    if expense is not None:
                        saved = save_entry(expense, chat_id)

                        if saved:
                            payload = {
                                'chat_id': chat_id,
                                'text': f'Saved: {expense["name"]} ({CURRENCY}{expense["amount"]:.2f}) [{expense["category"]}]'
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

                except Exception:
                    logger.exception('Photo processing failed')
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Error: could not process photo'
                    }

                send_message(chat_id, payload["text"])

                with open(UPDATE_FILE, 'w') as f:
                    f.write(str(update_id))

                offset = update_id + 1
                continue
            
            # ===== NON-TEXT MESSAGE =====
            elif 'text' not in message:
                payload = {
                    'chat_id': chat_id,
                    'text': 'Only text and photo messages are supported'
                }
                send_message(chat_id, payload["text"])

                with open(UPDATE_FILE, 'w') as f:
                    f.write(str(update_id))
                offset = update_id + 1
                continue
            
            # ===== TEXT MESSAGE =====
            text = message['text']

            # ===== COMMANDS =====
            if text in COMMAND_HANDLERS:
                payload = COMMAND_HANDLERS[text](chat_id)
                
            # ===== COMMAND: INCOME =====       
            elif text.startswith('/income'):
                payload = handle_income(chat_id, text)
            
            # ===== COMMAND: DELETE BY NUMBER =====
            elif text.startswith('/delete '):
                payload = handle_delete_by_number(chat_id, text)
            
            # ===== COMMAND: EDIT =====
            elif text.startswith('/edit '):
                payload = handle_edit(chat_id, text)
                    
            # ===== COMMAND: EXPORT =====        
            elif text == '/export':
                handle_export(chat_id)

                with open(UPDATE_FILE, 'w') as f:
                    f.write(str(update_id))
                offset = update_id + 1
                continue
               
            # ===== DEFAULT: PARSE EXPENSE TEXT =====    
            else:
                payload = handle_expense_text(chat_id, text)

            send_message(chat_id, payload["text"])

            with open(UPDATE_FILE, 'w') as f:
                f.write(str(update_id))
            offset = update_id + 1

        time.sleep(0.1)

except KeyboardInterrupt:
    logger.info('Bot stopped')

