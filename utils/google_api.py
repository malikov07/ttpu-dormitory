"""Google API utilities for Sheets."""

import asyncio
import io
import logging
from datetime import datetime
from pathlib import Path

from aiogram import Bot
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import SPREADSHEET_ID, CHANNEL_ID
from utils.applied_store import seed
from utils.lang_store import get_user_lang, save_user_lang
from utils.preview import format_phone, seed_counter

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"


def _safe_cell(value):
    """Neutralize spreadsheet formula injection in user-provided text.

    With valueInputOption=USER_ENTERED, a cell starting with = + - @ is treated
    as a formula. Prefix such user text with an apostrophe so Sheets stores it
    literally. Does not touch values we intentionally write as formulas.
    """
    if isinstance(value, str) and value and value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def get_services():
    """Initialize and return Google Sheets services."""
    try:
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        sheets_service = build("sheets", "v4", credentials=credentials)
        return sheets_service
    except Exception as e:
        logger.error(f"Failed to initialize Google API services: {e}")
        return None


import re

LINK_BLUE = {"red": 0.066, "green": 0.333, "blue": 0.8}


def _link_cell_request(sheet_id: int, row_index: int, url: str) -> dict:
    """Make column K a real clickable hyperlink.

    Written as a text-format run rather than a =HYPERLINK() formula: formula
    argument separators depend on the spreadsheet locale ("," vs ";"), so the
    formula silently lands as plain text in some locales. A link run is what the
    "Insert link" menu produces and is locale-independent.
    """
    return {
        "updateCells": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_index,
                "endRowIndex": row_index + 1,
                "startColumnIndex": 10,  # Column K = Telegram Link
                "endColumnIndex": 11,
            },
            "rows": [
                {
                    "values": [
                        {
                            "userEnteredValue": {"stringValue": url},
                            "textFormatRuns": [
                                {
                                    "startIndex": 0,
                                    "format": {
                                        "link": {"uri": url},
                                        "foregroundColor": LINK_BLUE,
                                        "underline": True,
                                    },
                                }
                            ],
                        }
                    ]
                }
            ],
            "fields": "userEnteredValue,textFormatRuns",
        }
    }


def _append_to_spreadsheet_sync(
    sheets_service, row_data: list, level: str, telegram_url: str = ""
):
    """Synchronous function to append a row to the spreadsheet and apply formatting."""
    body = {"values": [row_data]}
    response = sheets_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1", # Assumes the first sheet is named Sheet1
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    # Apply background color based on level
    updated_range = response.get("updates", {}).get("updatedRange", "")
    match = re.search(r"![A-Z]+(\d+)", updated_range)
    if match:
        row_num = int(match.group(1))
        row_index = row_num - 1 # 0-based index

        # Get sheetId
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']

        # Determine color (light pastel colors)
        color = {"red": 1.0, "green": 1.0, "blue": 1.0} # White default
        if "1" in level:
            color = {"red": 0.85, "green": 0.92, "blue": 1.0} # Light blue
        elif "2" in level:
            color = {"red": 0.85, "green": 0.96, "blue": 0.85} # Light green
        elif "3" in level:
            color = {"red": 1.0, "green": 0.96, "blue": 0.85} # Light yellow
        elif "4" in level:
            color = {"red": 1.0, "green": 0.85, "blue": 0.85} # Light red

        format_request = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(row_data)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": color,
                                "textFormat": {
                                    "foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0},
                                    "bold": False
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat)"
                    }
                },
            ]
        }
        # Applied after the row-wide format above, so the link run wins on column K.
        if telegram_url:
            format_request["requests"].append(
                _link_cell_request(sheet_id, row_index, telegram_url)
            )

        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=format_request
        ).execute()


async def process_and_save_application(bot: Bot, data: dict, app_id: int, msg_id: int):
    """Orchestrate saving data to Sheets."""
    sheets_service = get_services()
    if not sheets_service:
        logger.error("Could not obtain Google Services.")
        return

    # Prepare telegram deep link. The URL goes in as plain text; the cell is turned
    # into a clickable link by _link_cell_request after the row is appended.
    channel_str = str(CHANNEL_ID)
    if channel_str.startswith("-100"):
        # Private channel deep link: https://t.me/c/123456789/msg_id
        clean_channel_id = channel_str[len("-100"):]
        telegram_url = f"https://t.me/c/{clean_channel_id}/{msg_id}"
    elif channel_str.startswith("@"):
        # Public channel deep link: https://t.me/channelname/msg_id
        telegram_url = f"https://t.me/{channel_str[1:]}/{msg_id}"
    else:
        telegram_url = ""
    telegram_link = telegram_url or "N/A"

    # Columns: A=ID, B=Name, C=Sex, D=Level, E=Faculty, F=Region, G=Town,
    # H=Reason, I=Phone, J=Additional Phone, K=Telegram Link, L=Telegram ID,
    # M=Decision (admin fills: 1=accepted)
    level_str = data.get("level", "")
    full_name = data.get("full_name", "").title()
    sex_uz = data.get("sex_uz", "")
    additional_phone_raw = data.get("additional_phone", "") or ""
    row_data = [
        app_id,
        _safe_cell(full_name),
        _safe_cell(sex_uz),
        _safe_cell(level_str),
        _safe_cell(data.get("faculty_uz", data.get("faculty_name", ""))),
        _safe_cell(data.get("region_uz", data.get("region_name", ""))),
        _safe_cell(data.get("town_uz", data.get("town_name", ""))),
        _safe_cell(data.get("reason_uz", data.get("reason_name", ""))),
        _safe_cell(format_phone(data.get("phone", ""))),
        _safe_cell(format_phone(additional_phone_raw)) if additional_phone_raw else "",
        telegram_link,  # K = plain URL text; linked by _link_cell_request below
        str(data.get("user_id", "")),  # L = Telegram ID for messaging
    ]

    # Persist language locally so result messages are sent in the user's language.
    user_id = data.get("user_id")
    if user_id:
        save_user_lang(int(user_id), data.get("lang", "uz"))

    try:
        await asyncio.to_thread(
            _append_to_spreadsheet_sync, sheets_service, row_data, level_str, telegram_url
        )
        logger.info(f"Successfully saved application {app_id} to Google Sheets.")
    except Exception as e:
        logger.error(f"Failed to append data to Spreadsheet for app {app_id}: {e}")


def _read_applicant_ids_sync(sheets_service) -> list:
    """Read L=Telegram ID for every row that has one."""
    response = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!L1:L",
    ).execute()
    ids = []
    for row in response.get("values", []):
        raw = row[0].strip() if row and row[0] else ""
        if not raw:
            continue
        try:
            ids.append(int(float(raw)))
        except (ValueError, TypeError):
            continue  # header row or stray text
    return ids


async def sync_applied_users() -> int:
    """Seed the local applied-users record from the spreadsheet.

    Called at startup so applicants already in the sheet stay blocked from
    re-applying, even if the local file was never written or has been lost.
    Returns how many ids were newly recorded.
    """
    sheets_service = get_services()
    if not sheets_service:
        logger.error("Could not obtain Google Services to sync applied users.")
        return 0

    try:
        ids = await asyncio.to_thread(_read_applicant_ids_sync, sheets_service)
    except Exception as e:
        logger.error(f"Failed to read applicant ids from spreadsheet: {e}")
        return 0

    return seed(ids)


def _read_highest_app_id_sync(sheets_service) -> int:
    """Return the largest application id in column A, or 0 if there are none."""
    response = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A1:A",
    ).execute()
    highest = 0
    for row in response.get("values", []):
        raw = row[0].strip() if row and row[0] else ""
        if not raw:
            continue
        try:
            highest = max(highest, int(float(raw)))
        except (ValueError, TypeError):
            continue  # header row or stray text
    return highest


async def sync_app_counter() -> int:
    """Align the local id counter with the spreadsheet at startup.

    The counter file is local state; on a fresh or restored host it would otherwise
    restart at 1 and hand out ids that already exist in the sheet. Returns the id the
    counter now sits at, or 0 if the sheet could not be read.
    """
    sheets_service = get_services()
    if not sheets_service:
        logger.error("Could not obtain Google Services to sync the id counter.")
        return 0

    try:
        highest = await asyncio.to_thread(_read_highest_app_id_sync, sheets_service)
    except Exception as e:
        logger.error(f"Failed to read the highest application id from spreadsheet: {e}")
        return 0

    if seed_counter(highest):
        logger.warning(
            "Application id counter was behind the sheet — advanced it to %d.", highest
        )
    return highest


def _read_results_sync(sheets_service) -> list:
    """Read L=Telegram ID and M=Decision from the sheet.

    Returns a list of (telegram_id, accepted) for rows with a numeric ID.
    Non-numeric cells (e.g. a header row) are skipped automatically.
    """
    response = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!L1:M",
    ).execute()
    rows = response.get("values", [])
    results = []
    for row in rows:
        tg_id_raw = row[0].strip() if len(row) > 0 and row[0] else ""
        decision  = row[1].strip() if len(row) > 1 and row[1] else ""
        if not tg_id_raw:
            continue
        try:
            tg_id = int(float(tg_id_raw))
        except (ValueError, TypeError):
            continue
        results.append((tg_id, decision == "1"))
    return results


async def publish_results(bot: Bot) -> dict:
    """Send result messages to every applicant in their own language.

    Language is looked up from the local user_langs.json file saved at submit time.
    Returns a dict with counts: {"success", "failure", "failed"}.
    """
    from texts import t

    counts = {"success": 0, "failure": 0, "failed": 0}
    sheets_service = get_services()
    if not sheets_service:
        logger.error("Could not obtain Google Services for publishing results.")
        return counts

    try:
        results = await asyncio.to_thread(_read_results_sync, sheets_service)
    except Exception as e:
        logger.error(f"Failed to read results from spreadsheet: {e}")
        return counts

    for tg_id, accepted in results:
        lang = get_user_lang(tg_id)
        text = t("result_success" if accepted else "result_failure", lang)
        try:
            await bot.send_message(chat_id=tg_id, text=text, parse_mode="HTML")
            counts["success" if accepted else "failure"] += 1
        except Exception as e:
            counts["failed"] += 1
            logger.warning(f"Could not send result to {tg_id}: {e}")
        await asyncio.sleep(0.05)  # gentle rate limiting

    return counts
