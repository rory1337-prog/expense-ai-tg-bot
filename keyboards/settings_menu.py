from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

settings_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🌍 Language", callback_data="settings_language"),
            InlineKeyboardButton(text="💱 Currency", callback_data="settings_currency")
        ]
    ]
)

language_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="English", callback_data="set_lang:en"),
            InlineKeyboardButton(text="Русский", callback_data="set_lang:ru"),
            InlineKeyboardButton(text="Polski", callback_data="set_lang:pl")
        ]
    ]
)

currency_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="PLN", callback_data="set_currency:PLN"),
            InlineKeyboardButton(text="EUR", callback_data="set_currency:EUR"),
            InlineKeyboardButton(text="USD", callback_data="set_currency:USD")
        ]
    ]
)