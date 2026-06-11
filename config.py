import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
OFERTA_URL = os.getenv("OFERTA_URL", "")

# Comma-separated Telegram user IDs allowed to publish results, e.g. "12345,67890"
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x}


def is_admin(user_id: int) -> bool:
    """Return True if the given Telegram user id is an admin."""
    return user_id in ADMIN_IDS
