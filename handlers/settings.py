from aiogram import Router
from aiogram.types import Message, CallbackQuery

from database import get_user_settings, set_user_language, set_user_currency
from keyboards.settings_menu import (
    build_settings_menu,
    build_language_menu,
    build_currency_menu
)
from locales import t
from keyboards.buttons import b
from keyboards.main_menu import build_main_menu

router = Router()


@router.message(lambda message: message.text in [
    b("settings", "en"),
    b("settings", "ru"),
    b("settings", "pl"),
])
async def settings_handler(message: Message):
    settings = get_user_settings(message.chat.id)
    lang = settings["language"]

    print("SETTINGS LANG:", lang)
    print("SETTINGS:", settings)

    await message.answer(
        f"{t('settings', lang)}\n\n"
        f"{t('language', lang)}: {settings['language']}\n"
        f"{t('currency', lang)}: {settings['currency']}",
        reply_markup=build_settings_menu(lang)
    )


@router.callback_query(lambda c: c.data == "settings_language")
async def settings_language_callback(callback: CallbackQuery):
    settings = get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    await callback.message.answer(
        t("choose_language", lang),
        reply_markup=build_language_menu()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_currency")
async def settings_currency_callback(callback: CallbackQuery):
    settings = get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    await callback.message.answer(
        t("choose_currency", lang),
        reply_markup=build_currency_menu()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("set_lang:"))
async def set_language_callback(callback: CallbackQuery):
    language = callback.data.split(":")[1]

    set_user_language(callback.message.chat.id, language)

    await callback.message.answer(
        f"{t('language_set', language)} {language}",
        reply_markup=build_main_menu(language)
    )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("set_currency:"))
async def set_currency_callback(callback: CallbackQuery):
    currency = callback.data.split(":")[1]

    set_user_currency(callback.message.chat.id, currency)

    settings = get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    await callback.message.answer(
        f"{t('currency_set', lang)} {currency}"
    )

    await callback.answer()

@router.callback_query(lambda c: c.data == "settings_help")
async def settings_help_callback(callback: CallbackQuery):
    settings = get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    await callback.message.answer(t("help_text", lang))
    await callback.answer()