# ===== IMPORTS =====
import requests
from config import (
    BOT_TOKEN,
    TELEGRAM_URL,
    TELEGRAM_DOCUMENT_URL
)
from pathlib import Path

# ===== SEND MESSAGE =====
def send_message(chat_id,text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(TELEGRAM_URL, data=payload, timeout=10)

# ===== SEND DOCUMENT =====
def send_document(chat_id, file_path):
    with open(file_path, 'rb') as f:
        return requests.post(
            TELEGRAM_DOCUMENT_URL,
            data={'chat_id': chat_id},
            files={'document': f},
            timeout=20
        )
    
# ===== GET UPDATES =====
def get_updates(offset):
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
        params = {}

        if offset is not None:
            params['offset'] = offset

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    
    except Exception as e:
        print('GET UPDATES ERROR:', e)
        return {'result': []}
    
# ===== DOWNLOAD PHOTO =====
def download_photo(file_id, update_id):
    try:
        photo_url = (
            f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}'
        )

        response = requests.get(photo_url, timeout=20)
        response.raise_for_status()

        file_data = response.json()

        file_path = file_data["result"]["file_path"]

        download_url = (
            f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
        )

        file_response = requests.get(download_url, timeout=30)
        file_response.raise_for_status()

        receipt_file = Path(__file__).with_name(
            f"receipt_{update_id}.jpg"
        )

        with open(receipt_file, 'wb') as f:
            f.write(file_response.content)

        return receipt_file

    except Exception as e:
        print("DOWNLOAD PHOTO ERROR:", e)
        return None