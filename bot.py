# ===== IMPORTS =====
import time

from telegram_api import (
    send_message,
    send_document,
    get_updates,
    download_photo
)

from config import UPDATE_FILE, CURRENCY

from database import (
    save_expense,
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
            time.sleep(0.5)
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
                        saved = save_expense(expense, chat_id)

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

                except Exception as e:
                    print("PHOTO PROCESSING ERROR:", e)
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
                        
                        '📷 You can also send a receipt photo\n\n'

                        '🧪 ExpensesAI is currently in beta.\n'
                        'Feedback helps improve the bot:\n'
                        '@grindbtco'
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
                income = parse_income(text)

                if income is None:
                    payload = {
                        'chat_id': chat_id,
                        'text': 'Incorrect format. Use: /income salary 3000'  
                    }
                else:
                    saved = save_expense(income, chat_id)

                    if saved:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Saved income: {income["name"]} ({CURRENCY}{income["amount"]})'
                        }
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': "Error: could not save income"
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
                        'text': f'Deleted: {deleted["name"]} ({CURRENCY}{deleted["amount"]}) [{deleted["category"]}]'
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
                            'text': f'Deleted: {deleted["name"]} ({CURRENCY}{deleted["amount"]}) [{deleted["category"]}]'
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
                    
                    if len(parts) < 4:
                        raise ValueError
                    
                    number = int(parts[1])
                    amount = float(parts[-1])
                    name = ' '.join(parts[2:-1]).strip()

                    if amount <= 0 or not name:
                        raise ValueError

                    updated = update_entry_by_number(chat_id, number, name, amount)

                    if updated is None:
                        payload = {
                            'chat_id': chat_id,
                            'text': 'Invalid entry number'
                        }
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': f'Updated: {updated["name"]} ({CURRENCY}{updated["amount"]}) [{updated["category"]}]'
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
                    send_message(chat_id, payload["text"])
                else:
                    send_document(chat_id, export_file)
                    export_file.unlink(missing_ok=True)
                    with open(UPDATE_FILE, 'w') as f:
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
                            'text': f'Saved: {expense["name"]} ({CURRENCY}{expense["amount"]}) [{expense["category"]}]'
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

            send_message(chat_id, payload["text"])

            with open(UPDATE_FILE, 'w') as f:
                f.write(str(update_id))
            offset = update_id + 1

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Bot Stopped")

