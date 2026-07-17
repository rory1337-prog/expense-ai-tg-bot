import logging
from pathlib import Path
from uuid import uuid4

from aiogram import Router
from aiogram.types import Message

from ai import ai_parse_photo
from locales import t
from locales.categories import localize_category
from services.expense_service import ExpenseService
from services.settings_service import SettingsService

logger = logging.getLogger(__name__)

router = Router()

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


def build_receipt_response(entry, currency, lang):
    response_text = (
        f"{t('receipt_saved', lang)}:\n"
        f"{entry['name']} — {entry['amount']:.2f} {currency}\n"
        f"{t('category', lang)}: {localize_category(entry['category'], lang)}\n"
    )

    items = entry.get("items", [])

    if items:
        response_text += "\n🧾 Items:\n"

        for item in items:
            response_text += (
                f"• {item['name']} — {float(item['amount']):.2f} {currency}\n"
            )

    return response_text


@router.message(lambda message: message.photo)
async def photo_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]
    currency = settings["currency"]

    await message.answer(t("receipt_received", lang))

    if not message.photo or message.bot is None:
        await message.answer(t("failed_parse_receipt", lang))
        return

    file_path = TEMP_DIR / f"{uuid4()}.jpg"

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)

        if not file.file_path:
            await message.answer(t("failed_parse_receipt", lang))
            return

        await message.bot.download_file(
            file.file_path,
            destination=file_path,
        )

        entry = await ai_parse_photo(str(file_path))

        if not entry:
            await message.answer(t("failed_parse_receipt", lang))
            return

        ok = ExpenseService.save_entry(entry, message.chat.id)

        if ok:
            await message.answer(build_receipt_response(entry, currency, lang))
        else:
            await message.answer(t("failed_save_receipt", lang))

    except Exception:
        logger.exception(
            "Receipt handler failed for chat_id=%s",
            message.chat.id,
        )
        await message.answer(t("failed_parse_receipt", lang))

    finally:
        file_path.unlink(missing_ok=True)
