"""TTPU Dormitory Application Bot — Entry Point."""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, RESULT_POLL_SECONDS
from handlers import start, menu, application, admin
from utils.google_api import sync_app_counter, sync_applied_users
from utils.results import results_watcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize and start the bot."""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN is not set! Please set it in .env file.")
        sys.exit(1)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers — order matters!
    # application router first so cancel handler catches during form states
    dp.include_router(application.router)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(menu.router)

    # Pick up applicants already in the sheet so they cannot apply a second time.
    added = await sync_applied_users()
    logger.info("Synced %d previously-recorded applicant(s) from the spreadsheet.", added)

    # Keep the id sequence continuous across host moves — the counter is local state.
    highest = await sync_app_counter()
    logger.info("Application ids resume after %d.", highest)

    logger.info("Bot is starting...")
    # Discard updates queued while the bot was down. The FSM lives in memory, so any
    # form in progress is gone on restart and replaying those messages only confuses
    # people. Must be done here: start_polling has no drop_pending_updates parameter,
    # and passing one there is silently absorbed into **kwargs.
    await bot.delete_webhook(drop_pending_updates=True)

    # Watches the sheet for finished decisions and delivers them on its own.
    watcher = asyncio.create_task(results_watcher(bot, RESULT_POLL_SECONDS))
    try:
        await dp.start_polling(bot)
    finally:
        watcher.cancel()


if __name__ == "__main__":
    asyncio.run(main())
