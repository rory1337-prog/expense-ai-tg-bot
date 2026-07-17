from aiogram import Router
from aiogram.types import CallbackQuery, Message

from keyboards.buttons import b
from keyboards.main_menu import build_main_menu
from keyboards.settings_menu import (
    build_currency_menu,
    build_language_menu,
    build_settings_menu,
)
from locales import t
from services.settings_service import SettingsService

router = Router()


@router.message(
    lambda message: (
        message.text
        in [
            b("settings", "en"),
            b("settings", "ru"),
            b("settings", "pl"),
        ]
    )
)
async def settings_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(
        f"{t('settings', lang)}\n\n"
        f"{t('language', lang)}: {settings['language']}\n"
        f"{t('currency', lang)}: {settings['currency']}",
        reply_markup=build_settings_menu(lang),
    )


@router.callback_query(lambda c: c.data == "settings_language")
async def settings_language_callback(callback: CallbackQuery):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    message = callback.message

    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(
        t("choose_language", lang),
        reply_markup=build_language_menu(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_currency")
async def settings_currency_callback(callback: CallbackQuery):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    message = callback.message

    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(
        t("choose_currency", lang),
        reply_markup=build_currency_menu(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("set_lang:"))
async def set_language_callback(callback: CallbackQuery):
    if not isinstance(callback.message, Message) or callback.data is None:
        await callback.answer()
        return

    message = callback.message
    language = callback.data.split(":", maxsplit=1)[1]

    SettingsService.set_user_language(message.chat.id, language)

    await message.answer(
        f"{t('language_set', language)} {language}",
        reply_markup=build_main_menu(language),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("set_currency:"))
async def set_currency_callback(callback: CallbackQuery):
    if not isinstance(callback.message, Message) or callback.data is None:
        await callback.answer()
        return

    message = callback.message
    currency = callback.data.split(":", maxsplit=1)[1]

    SettingsService.set_user_currency(message.chat.id, currency)

    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(f"{t('currency_set', lang)} {currency}")
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings_help")
async def settings_help_callback(callback: CallbackQuery):
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    message = callback.message

    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(t("help_text", lang))
    await callback.answer()
