from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards.buttons import b


def build_main_menu(lang="en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=b("reports", lang)),
                KeyboardButton(text=b("edit", lang)),
            ],
            [KeyboardButton(text=b("settings", lang))],
        ],
        resize_keyboard=True,
    )
