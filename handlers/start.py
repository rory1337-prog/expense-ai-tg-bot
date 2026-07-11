from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import build_main_menu
from locales import detect_language, t
from services.settings_service import SettingsService

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    chat_id = message.chat.id

    telegram_lang = message.from_user.language_code
    detected_lang = detect_language(telegram_lang)

    SettingsService.ensure_user_settings(chat_id, language=detected_lang)

    settings = SettingsService.get_user_settings(chat_id)
    lang = settings["language"]

    await message.answer(
        f"{t('start', lang)}\n\n{t('help_text', lang)}",
        reply_markup=build_main_menu(lang),
    )
