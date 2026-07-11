from aiogram import Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.buttons import b
from keyboards.reports_menu import build_reports_menu
from locales import t
from reports import (
    build_analytics,
    build_balance,
    build_period_report,
    build_report,
    export_data,
)
from services.settings_service import SettingsService

router = Router()


@router.message(
    lambda message: (
        message.text
        in [
            b("reports", "en"),
            b("reports", "ru"),
            b("reports", "pl"),
        ]
    )
)
async def reports_handler(message: Message):
    settings = SettingsService.get_user_settings(message.chat.id)
    lang = settings["language"]

    await message.answer(
        f"{t('reports_menu', lang)}\n\nCurrency: {settings['currency']}",
        reply_markup=build_reports_menu(lang),
    )


@router.callback_query(lambda c: c.data == "today")
async def today_callback(callback: CallbackQuery):
    report = build_period_report(callback.message.chat.id, "today")
    await callback.message.answer(report)
    await callback.answer()


@router.callback_query(lambda c: c.data == "week")
async def week_callback(callback: CallbackQuery):
    report = build_period_report(callback.message.chat.id, "week")
    await callback.message.answer(report)
    await callback.answer()


@router.callback_query(lambda c: c.data == "month")
async def month_callback(callback: CallbackQuery):
    report = build_period_report(callback.message.chat.id, "month")
    await callback.message.answer(report)
    await callback.answer()


@router.callback_query(lambda c: c.data == "all")
async def all_callback(callback: CallbackQuery):
    report = build_report(callback.message.chat.id)
    await callback.message.answer(report)
    await callback.answer()


@router.callback_query(lambda c: c.data == "balance")
async def balance_callback(callback: CallbackQuery):
    report = build_balance(callback.message.chat.id)
    await callback.message.answer(report)
    await callback.answer()


@router.callback_query(lambda c: c.data == "analytics")
async def analytics_callback(callback: CallbackQuery):
    report = build_analytics(callback.message.chat.id)
    await callback.message.answer(report)
    await callback.answer()


@router.callback_query(lambda c: c.data == "export")
async def export_callback(callback: CallbackQuery):
    export_file = export_data(callback.message.chat.id)

    settings = SettingsService.get_user_settings(callback.message.chat.id)
    lang = settings["language"]

    if not export_file:
        await callback.message.answer(t("no_data_export", lang))
        await callback.answer()
        return

    document = FSInputFile(export_file)

    await callback.message.answer_document(document)
    await callback.answer()
