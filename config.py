import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

# Every timestamp the tutors and applicants see is Tashkent time. Written as a
# fixed +5 offset rather than a named zone: Uzbekistan has no daylight saving,
# and a plain offset needs no tz database on the host.
TASHKENT_TZ = timezone(timedelta(hours=5), "UTC+5")


def now_tashkent() -> datetime:
    """Current local time in Tashkent, wherever the server happens to run."""
    return datetime.now(TASHKENT_TZ)

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

# Machine-translate the reason tutors write into each applicant's own language,
# with the tutor's original sent underneath it. Set to 0 to send the reason
# exactly as typed. On by default: the bot degrades to the original text on its
# own if the Translation API is not reachable.
TRANSLATE_REASONS = os.getenv("TRANSLATE_REASONS", "1").strip().lower() not in (
    "0",
    "false",
    "no",
    "off",
)

# Free Gemini key from https://aistudio.google.com/apikey — no card, no billing
# account. Leave it empty and reasons simply go out as the tutors typed them.
# Never enable billing on the Google project this key belongs to: that deletes
# its free tier and every call starts billing from the first token.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()


def is_admin(user_id: int) -> bool:
    """Return True if the given Telegram user id is an admin."""
    return user_id in ADMIN_IDS
