from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from locales import t


def build_settings_menu(lang="en"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🌍 {t('language', lang)}", callback_data="settings_language"
                ),
                InlineKeyboardButton(
                    text=f"💱 {t('currency', lang)}", callback_data="settings_currency"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"ℹ️ {t('help', lang)}", callback_data="settings_help"
                )
            ],
        ]
    )


def build_language_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="English", callback_data="set_lang:en"),
                InlineKeyboardButton(text="Русский", callback_data="set_lang:ru"),
                InlineKeyboardButton(text="Polski", callback_data="set_lang:pl"),
            ]
        ]
    )


def build_currency_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="PLN", callback_data="set_currency:PLN"),
                InlineKeyboardButton(text="EUR", callback_data="set_currency:EUR"),
                InlineKeyboardButton(text="USD", callback_data="set_currency:USD"),
            ]
        ]
    )
