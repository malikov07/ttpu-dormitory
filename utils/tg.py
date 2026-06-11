"""Small Telegram helper utilities."""

import logging
from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


async def safe_delete(message) -> None:
    """Delete a message, ignoring 'message to delete not found' and similar errors.

    Messages can fail to delete when they are already gone, older than 48h, or
    when a button is tapped twice. None of these should crash a handler.
    """
    if message is None:
        return
    with suppress(TelegramBadRequest):
        await message.delete()
