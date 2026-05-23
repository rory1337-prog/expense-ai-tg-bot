from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Add expense")],
        [KeyboardButton(text="📊 Reports"), KeyboardButton(text="✏️ Edit")],
        [KeyboardButton(text="⚙️ Settings")]
    ],
    resize_keyboard=True
)