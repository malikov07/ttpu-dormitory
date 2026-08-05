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

# How often the bot re-reads the sheet looking for finished decisions.
RESULT_POLL_SECONDS = int(os.getenv("RESULT_POLL_SECONDS", "120"))

# How long a status + reason must stay unchanged before the result is sent.
# This is what stops a half-typed reason from reaching a student: every edit
# restarts the clock, so tutors can take as long as they like over the wording.
RESULT_QUIET_SECONDS = int(os.getenv("RESULT_QUIET_SECONDS", "600"))


def is_admin(user_id: int) -> bool:
    """Return True if the given Telegram user id is an admin."""
    return user_id in ADMIN_IDS
