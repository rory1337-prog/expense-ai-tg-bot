from pathlib import Path
from uuid import uuid4

from aiogram import Router
from aiogram.types import Message

from ai import ai_parse_photo
from services.expense_service import ExpenseService
from services.settings_service import SettingsService
from locales import t
from locales.categories import localize_category

router = Router()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

def build_receipt_response(entry, currency, lang):
    response_text = (
        f"{t('receipt_saved', lang)}:\n"
        f"{entry['name']} — {entry['amount']:.2f} {currency}\n"
        f"{t('category', lang)}: {localize_category(entry['category'], lang)}\n"
    )

    items = entry.get('items', [])

    if items:
        response_text += "\n🧾 Items:\n"

        for item in items:
            response_text += (
                f"• {item['name']} — "
                f"{float(item['amount']):.2f} {currency}\n"
            )

    return response_text

@router.message(lambda message: message.photo)
async def photo_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    await message.answer(t("receipt_received", lang))

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    file_path = TEMP_DIR / f"{uuid4()}.jpg"

    await message.bot.download_file(file.file_path, destination=file_path)

    entry = await ai_parse_photo(str(file_path))

    file_path.unlink(missing_ok=True)

    if not entry:
        await message.answer(t("failed_parse_receipt", lang))
        return

    ok = ExpenseService.save_entry(entry, message.chat.id)

    if ok:
        await message.answer(build_receipt_response(entry, currency, lang))

    else:
        await message.answer(t("failed_save_receipt", lang))