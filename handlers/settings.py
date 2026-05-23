from aiogram import Router
from aiogram.types import Message, CallbackQuery

from database import get_user_settings, set_user_language, set_user_currency
from keyboards.settings_menu import settings_menu, language_menu, currency_menu

router = Router()


@router.message(lambda message: message.text == "⚙️ Settings")
async def settings_handler(message: Message):
    settings = get_user_settings(message.chat.id)

    await message.answer(
        f"⚙️ Settings\n\nLanguage: {settings['language']}\nCurrency: {settings['currency']}",
        reply_markup=settings_menu
    )


@router.callback_query(lambda c: c.data == "settings_language")
async def settings_language_callback(callback: CallbackQuery):
    await callback.message.answer(
        "Choose language:",
        reply_markup=language_menu
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_currency")
async def settings_currency_callback(callback: CallbackQuery):
    await callback.message.answer(
        "Choose currency:",
        reply_markup=currency_menu
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("set_lang:"))
async def set_language_callback(callback: CallbackQuery):
    language = callback.data.split(":")[1]
    set_user_language(callback.message.chat.id, language)

    await callback.message.answer(f"✅ Language set to {language}")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("set_currency:"))
async def set_currency_callback(callback: CallbackQuery):
    currency = callback.data.split(":")[1]
    set_user_currency(callback.message.chat.id, currency)

    await callback.message.answer(f"✅ Currency set to {currency}")
    await callback.answer()