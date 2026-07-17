import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.ask import router as ask_router
from handlers.edit import router as edit_router
from handlers.expenses import router as expenses_router
from handlers.menu import router as menu_router
from handlers.photos import router as photos_router
from handlers.reports import router as reports_router
from handlers.settings import router as settings_router
from handlers.start import router as start_router

logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)
    dispatcher.include_router(menu_router)
    dispatcher.include_router(reports_router)
    dispatcher.include_router(edit_router)
    dispatcher.include_router(photos_router)
    dispatcher.include_router(settings_router)
    dispatcher.include_router(ask_router)
    dispatcher.include_router(expenses_router)

    return dispatcher


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOTTOKEN is not configured")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(token=BOT_TOKEN)
    dispatcher = create_dispatcher()

    logger.info("Starting ExpensesAI bot")

    try:
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    finally:
        logger.info("Stopping ExpensesAI bot")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
