from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_edit_menu(entries):
    buttons = []

    for entry in entries[:5]:
        text = f"{entry['name']} — {entry['amount']} PLN"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=text, callback_data=f"edit_select:{entry['id']}"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
