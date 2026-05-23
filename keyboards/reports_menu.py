from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

reports_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Today", callback_data="today"),
            InlineKeyboardButton(text="Week", callback_data="week")
        ],
        [
            InlineKeyboardButton(text="Month", callback_data="month"),
            InlineKeyboardButton(text="All", callback_data="all")
        ],
        [
            InlineKeyboardButton(text="Balance", callback_data="balance"),
            InlineKeyboardButton(text="Analytics", callback_data="analytics")
        ]
    ]
)