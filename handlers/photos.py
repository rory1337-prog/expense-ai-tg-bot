from pathlib import Path
from uuid import uuid4

from aiogram import Router
from aiogram.types import Message

from ai import ai_parse_photo
from database import save_entry, get_user_settings
from locales import t

router = Router()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


@router.message(lambda message: message.photo)
async def photo_handler(message: Message):
    settings = get_user_settings(message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    await message.answer(t("receipt_received", lang))

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    file_path = TEMP_DIR / f"{uuid4()}.jpg"

    await message.bot.download_file(file.file_path, destination=file_path)

    entry = ai_parse_photo(str(file_path))

    file_path.unlink(missing_ok=True)

    if not entry:
        await message.answer(t("failed_parse_receipt", lang))
        return

    ok = save_entry(entry, message.chat.id)

    if ok:
        await message.answer(
            f"{t('receipt_saved', lang)}:\n"
            f"{entry['name']} — {entry['amount']} {currency}\n"
            f"{t('category', lang)}: {entry['category']}"
        )
    else:
        await message.answer(t("failed_save_receipt", lang))