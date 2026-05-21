# ===== IMPORTS =====
import time
import logging

from handlers import (
    COMMAND_HANDLERS,
    handle_income,
    handle_delete_by_number,
    handle_edit,
    handle_export,
    handle_expense_text,
    handle_photo_message
)

from telegram_api import (
    send_message,
    get_updates
)

from config import UPDATE_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

logger = logging.getLogger(__name__)

# ===== TELEGRAM UPDATES =====
def save_offset(update_id):
    with open(UPDATE_FILE, 'w') as f:
        f.write(str(update_id))

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
                save_offset(update_id)
                offset = update_id + 1
                continue

            chat_id = str(message['chat']['id'])

            # ===== PHOTO MESSAGE =====
            if 'photo' in message:
                payload = handle_photo_message(chat_id, message, update_id)

                send_message(chat_id, payload['text'])

                save_offset(update_id)
                offset = update_id + 1
                continue
            
            # ===== NON-TEXT MESSAGE =====
            elif 'text' not in message:
                payload = {
                    'chat_id': chat_id,
                    'text': 'Only text and photo messages are supported'
                }
                send_message(chat_id, payload["text"])

                save_offset(update_id)
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

                save_offset(update_id)
                offset = update_id + 1
                continue
               
            # ===== DEFAULT: PARSE EXPENSE TEXT =====    
            else:
                payload = handle_expense_text(chat_id, text)

            send_message(chat_id, payload["text"])

            save_offset(update_id)
            offset = update_id + 1

        time.sleep(0.1)

except KeyboardInterrupt:
    logger.info('Bot stopped')

