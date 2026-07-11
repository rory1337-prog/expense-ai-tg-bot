from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from locales import t


def build_reports_menu(lang="en"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("today", lang), callback_data="today"),
                InlineKeyboardButton(text=t("week", lang), callback_data="week"),
            ],
            [
                InlineKeyboardButton(text=t("month", lang), callback_data="month"),
                InlineKeyboardButton(text=t("all", lang), callback_data="all"),
            ],
            [
                InlineKeyboardButton(text=t("balance", lang), callback_data="balance"),
                InlineKeyboardButton(
                    text=t("analytics", lang), callback_data="analytics"
                ),
            ],
            [InlineKeyboardButton(text=t("export", lang), callback_data="export")],
        ]
    )
