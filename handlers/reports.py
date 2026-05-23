from aiogram import Router
from aiogram.types import Message, CallbackQuery

from keyboards.reports_menu import reports_menu
from reports import (
    build_report,
    build_period_report,
    build_balance,
    build_analytics
)

from database import get_user_settings

router = Router()


@router.message(lambda message: message.text == "📊 Reports")
async def reports_handler(message: Message):
    settings = get_user_settings(message.chat.id)

    await message.answer(
        f"📊 Reports Menu\n\nCurrency: {settings['currency']}",
        reply_markup=reports_menu
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