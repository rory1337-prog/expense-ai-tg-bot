from pathlib import Path
from uuid import uuid4

from aiogram import Router
from aiogram.types import Message

from ai import ai_parse_photo
from database import save_entry

router = Router()

TEMP_DIR = Path('temp')
TEMP_DIR.mkdir(exist_ok=True)

@router.message(lambda message: message.photo)
async def photo_handler(message: Message):
    print("PHOTO HANDLER TRIGGERED")
    await message.answer("📸 Receipt received. Parsing...")

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    file_path = TEMP_DIR / f'{uuid4()}.jpg'

    await message.bot.download_file(file.file_path, destination=file_path)

    entry = ai_parse_photo(str(file_path))

    file_path.unlink(missing_ok=True)

    if not entry:
        await message.answer("❌ Could not parse receipt.")
        return
    
    ok = save_entry(entry, message.chat.id)

    if ok:
        await message.answer(
            f"✅ Receipt saved:\n{entry['name']} — {entry['amount']} PLN\nCategory: {entry['category']}"
        )
    else:
        await message.answer("❌ Failed to save receipt.")