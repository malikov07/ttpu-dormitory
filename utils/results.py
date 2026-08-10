"""Delivering admission results to applicants, one row at a time.

Tutors fill in three columns per applicant:

    M = status   0 = not accepted, 1 = invited to an interview, 2 = accepted
    N = reason   free text, shown to the applicant
    O = sent     written by the bot: when the message went out, or why it did not

Status 0 and 2 are final and always need a reason. Status 1 does not: tutors mark
a row 1 as soon as they decide to interview someone, long before there is a date
to give them. Such a row goes out straight away as "you are invited, details to
follow", and when the tutor later fills N in with the date and whatever else the
applicant needs to know, that text is delivered as a second message.

Tutors also change their minds and correct themselves. Whenever M or N differs
from what the applicant was last told, the row is delivered again as a fresh
message marked as an update, so what the applicant has read always matches what
the sheet says.

A background watcher (see `results_watcher`) polls the sheet, so each applicant
hears back as soon as their own row is finished instead of waiting for a batch.

The detail that shapes this module: tutors type the reason straight into the cell
and Sheets saves every keystroke, so a poll that lands mid-sentence would ship
half a thought to a student — and a sent Telegram message cannot be recalled. A
row is therefore only delivered once its status and reason have stayed identical
for QUIET_SECONDS. Any edit restarts that timer, and that is also what makes
re-sending on every edit bearable: rewording a sentence costs the applicant one
message rather than ten, and an edit taken back within the quiet period costs
them nothing at all.
"""

import asyncio
import html
import json
import logging
import time
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from config import RESULT_QUIET_SECONDS, SPREADSHEET_ID, now_tashkent
from utils.google_api import get_services
from utils.lang_store import get_user_lang
from utils.translate import translate_reason

logger = logging.getLogger(__name__)

SHEET_NAME = "Sheet1"
STATE_FILE = Path(__file__).parent.parent / "results_state.json"

# 0-based column indexes into a sheet row.
COL_ID = 0  # A
COL_TELEGRAM_ID = 11  # L
COL_STATUS = 12  # M
COL_REASON = 13  # N
COL_SENT = 14  # O

# Which message each status gets, and which counter it lands in.
STATUS_TEXTS = {
    "2": ("result_accepted", "accepted"),
    "1": ("result_interview", "interview"),
    "0": ("result_rejected", "rejected"),
}

# Sent for status 1 when the tutors have not written anything in N yet.
INTERVIEW_NO_REASON = "result_interview_no_reason"

# Sent when that reason finally arrives, as a message of its own.
INTERVIEW_DETAILS = "result_interview_details"

# Give up on a row after this many failed attempts so a permanently unreachable
# applicant is not retried every couple of minutes forever.
MAX_ATTEMPTS = 3

# One delivery pass at a time: the watcher and the admin's "publish" button share
# this module, and two passes running together would send some results twice.
_lock = asyncio.Lock()

# Applications whose status cell holds something that is not 0, 1 or 2. Kept so a
# typo is reported when it appears and not on every pass for weeks afterwards.
_bad_status_seen: set = set()


# ---------------------------------------------------------------- local state
#
# One record per application id. The two fingerprints are what keep re-sending
# under control:
#
#     fingerprint       the status+reason last seen in the sheet, with `since`
#                       marking when it appeared — the quiet period runs on it
#     sent_fingerprint  the status+reason the applicant has actually been told
#
# They differ only while a tutor's edit is settling. A row is sent when the two
# disagree, which means an edit taken back before the quiet period is over is
# never sent — the applicant is already holding that text. Records written before
# re-sending existed have no `sent_fingerprint` and are backfilled on sight; see
# `deliver_ready_results`.

def _load_state() -> dict:
    """Read the per-applicant delivery record. A missing/corrupt file is empty."""
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("results_state.json is unreadable — treating it as empty.")
        return {}
    return data if isinstance(data, dict) else {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def _persist(state: dict) -> bool:
    """Save the state file. Reports failure instead of raising: a delivery pass
    that cannot write its record must still finish and log why."""
    try:
        _save_state(state)
        return True
    except Exception as e:
        logger.error(f"Failed to save the results state file: {e}")
        return False


def clear_sent(app_id: str) -> bool:
    """Forget that an applicant was told their result, so it is sent again.

    Returns False if there was nothing on record for that application id.
    """
    state = _load_state()
    if app_id not in state:
        return False
    del state[app_id]
    _save_state(state)
    return True


# ---------------------------------------------------------------- sheet access

def _cell(row: list, index: int) -> str:
    """Read one cell out of a sheet row. Short rows come back as short lists."""
    if len(row) <= index:
        return ""
    value = row[index]
    return value.strip() if isinstance(value, str) else str(value).strip()


def _normalize_status(raw: str):
    """Map a status cell to "0", "1" or "2"; None when it is not a decision.

    Sheets hands back whatever the cell is formatted as, so 1 may arrive as "1",
    "1.0" or "1,0". Anything else — blank, a note, a typo — means the tutors have
    not decided yet and the row is left alone.
    """
    text = raw.strip().replace(",", ".")
    if not text:
        return None
    try:
        value = int(float(text))
    except (ValueError, TypeError):
        return None
    return str(value) if value in (0, 1, 2) else None


def _read_rows_sync(sheets_service) -> list:
    """Read every applicant row, with the sheet row number each one sits on."""
    response = (
        sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A1:O")
        .execute()
    )

    rows = []
    for offset, raw_row in enumerate(response.get("values", [])):
        telegram_raw = _cell(raw_row, COL_TELEGRAM_ID)
        try:
            telegram_id = int(float(telegram_raw))
        except (ValueError, TypeError):
            continue  # header row, or a row the bot did not write

        app_id = _cell(raw_row, COL_ID)
        rows.append(
            {
                # Keyed by application id, not row number: tutors sort and filter
                # the sheet, which moves rows around between polls.
                "key": app_id or f"tg{telegram_id}",
                "row_number": offset + 1,
                "telegram_id": telegram_id,
                "status_raw": _cell(raw_row, COL_STATUS),
                "status": _normalize_status(_cell(raw_row, COL_STATUS)),
                "reason": _cell(raw_row, COL_REASON),
                "sent_cell": _cell(raw_row, COL_SENT),
            }
        )
    return rows


def _write_sent_column_sync(sheets_service, stamps: list) -> None:
    """Write the delivery notes back to column O in a single request."""
    sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "valueInputOption": "RAW",
            "data": [
                {"range": f"{SHEET_NAME}!O{row_number}", "values": [[note]]}
                for row_number, note in stamps
            ],
        },
    ).execute()


# ---------------------------------------------------------------- delivery

async def _render(
    text_key: str, telegram_id: int, reason: str, updated: bool = False
) -> str:
    """Build one message in the applicant's own language.

    The template comes from texts.py; the reason is a tutor's free text, so it is
    machine-translated to match. The tutor's exact words follow underneath —
    see utils/translate.py for why a translation never travels alone.

    `updated` puts a line on top saying this replaces what was sent before. An
    applicant who has already been told they were accepted must not be left
    guessing which of two contradictory messages is the current one.

    quote=False on purpose: messages go out as HTML, where only & < > need
    escaping. Escaping quotes too would turn every Uzbek o' and g' in the reason
    tutors wrote into &#x27;.
    """
    from texts import t

    lang = get_user_lang(telegram_id)
    shown, translated = await translate_reason(reason, lang)

    block = html.escape(shown, quote=False)
    if translated:
        block += t("reason_original", lang, original=html.escape(reason, quote=False))

    text = t(text_key, lang, reason=block)
    return t("result_updated", lang) + text if updated else text


async def _try_send(bot: Bot, telegram_id: int, text: str) -> tuple:
    """Deliver one message, sorting the ways it can fail.

    Returns (outcome, detail): "sent", "blocked" (the applicant cannot be reached
    and retrying will not change that), "flood" (Telegram asked us to slow down,
    so the pass should stop) or "error" (worth another attempt later).
    """
    try:
        await bot.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
    except TelegramRetryAfter as e:
        return "flood", str(e.retry_after)
    except (TelegramForbiddenError, TelegramBadRequest) as e:
        return "blocked", str(e)
    except Exception as e:  # network hiccup, Telegram 5xx, …
        return "error", str(e)
    return "sent", ""


async def deliver_ready_results(bot: Bot) -> dict:
    """Send results for every row that is decided, explained and settled.

    Returns counts: accepted / interview / rejected (delivered now), details
    (interview rows whose date and instructions went out as a follow-up), updated
    (a decision or reason changed after the applicant was told, and the new one
    went out), failed (delivery gave up), waiting (still inside the quiet period),
    no_details (invited to an interview, N still empty), pending (status or reason
    missing) and undecided (tutors have not touched the row).
    """
    counts = {
        "accepted": 0,
        "interview": 0,
        "rejected": 0,
        "details": 0,
        "updated": 0,
        "failed": 0,
        "waiting": 0,
        "no_details": 0,
        "pending": 0,
        "undecided": 0,
    }

    async with _lock:
        sheets_service = get_services()
        if not sheets_service:
            logger.error("Could not obtain Google Services to deliver results.")
            return counts

        try:
            rows = await asyncio.to_thread(_read_rows_sync, sheets_service)
        except Exception as e:
            logger.error(f"Failed to read result rows from the spreadsheet: {e}")
            return counts

        state = _load_state()
        now = time.time()
        stamps: list = []
        dirty = False
        bad_status = set()

        for row in rows:
            key = row["key"]
            record = state.get(key, {})
            status, reason = row["status"], row["reason"]

            if record.get("done") and "sent_fingerprint" not in record:
                # Written before re-sending existed: one fingerprint, and it was
                # the text the applicant was sent. Backfilled here, before the
                # code below has a chance to move `fingerprint` on to an edit —
                # get this wrong and everyone hears their result a second time.
                record["sent_fingerprint"] = record.get("fingerprint", "")
                record.pop("edited", None)  # the flag that stood in for this
                state[key] = record
                dirty = True

            if record.get("done") and record.get("awaiting_details") and status == "1":
                # Invited to an interview earlier with nothing to say yet.
                # The moment N holds settled text, it goes out on its own.
                if not reason:
                    counts["no_details"] += 1
                    continue

                fingerprint = f"{status}\x1f{reason}"
                if record.get("details_fingerprint") != fingerprint:
                    record.update(details_fingerprint=fingerprint, details_since=now)
                    state[key] = record
                    dirty = True
                    counts["waiting"] += 1
                    continue

                if now - record.get("details_since", now) < RESULT_QUIET_SECONDS:
                    counts["waiting"] += 1
                    continue

                outcome, detail = await _try_send(
                    bot,
                    row["telegram_id"],
                    await _render(INTERVIEW_DETAILS, row["telegram_id"], reason),
                )
                if outcome == "flood":
                    logger.warning(
                        "Telegram asked us to slow down (%ss) — pausing.", detail
                    )
                    break
                if outcome == "error":
                    attempts = record.get("details_attempts", 0) + 1
                    record["details_attempts"] = attempts
                    if attempts >= MAX_ATTEMPTS:
                        record.update(awaiting_details=False, error=detail)
                        counts["failed"] += 1
                        stamps.append(
                            (
                                row["row_number"],
                                f"{row['sent_cell']} ❌ suhbat ma'lumoti yuborilmadi: {detail}"[:200],
                            )
                        )
                        logger.error(
                            "Giving up on the interview details for %s after %d attempts: %s",
                            key, attempts, detail,
                        )
                    else:
                        logger.warning(
                            "Interview details for %s failed (attempt %d): %s",
                            key, attempts, detail,
                        )
                    state[key] = record
                    dirty = True
                    continue
                if outcome == "blocked":
                    logger.warning("Cannot reach applicant %s: %s", key, detail)
                    record.update(awaiting_details=False, error=detail)
                    state[key] = record
                    dirty = True
                    counts["failed"] += 1
                    stamps.append(
                        (
                            row["row_number"],
                            f"{row['sent_cell']} ❌ suhbat ma'lumoti yuborilmadi: bot bloklangan",
                        )
                    )
                    continue

                # Sent. This text is now what the applicant holds, so a further
                # edit is an update and goes out through the path below.
                record.update(
                    awaiting_details=False,
                    fingerprint=fingerprint,
                    sent_fingerprint=fingerprint,
                    details_sent_at=now_tashkent().isoformat(timespec="seconds"),
                )
                state[key] = record
                dirty = not _persist(state)
                counts["details"] += 1
                stamps.append(
                    (
                        row["row_number"],
                        f"{row['sent_cell']} 📅 {now_tashkent():%Y-%m-%d %H:%M}",
                    )
                )
                await asyncio.sleep(0.05)
                continue

            if status is None and row["status_raw"]:
                # Someone typed something else into the status cell — a 3, a note,
                # a stray character. Nothing is sent for it, so say so out loud.
                bad_status.add(key)

            if status is None and not reason and not row["status_raw"]:
                counts["undecided"] += 1
                continue

            if status is None or (status != "1" and not reason):
                # Half-filled: an accepted/rejected row without its explanation,
                # or the reason typed before the status. Wait for the tutor to
                # finish — including when the row has been delivered already and
                # a tutor has just cleared the cell to rewrite it. Status 1 is
                # exempt: an invitation is worth sending before anyone knows the
                # interview date.
                counts["pending"] += 1
                continue

            fingerprint = f"{status}\x1f{reason}"
            if record.get("fingerprint") != fingerprint:
                # First sight of this text, or the tutor is still editing —
                # restart the quiet period. Whatever the row was worth before,
                # the attempt count belongs to the text that failed, not this one.
                record.update(fingerprint=fingerprint, since=now, attempts=0)
                state[key] = record
                dirty = True
                counts["waiting"] += 1
                continue

            update = bool(record.get("done"))
            if update and record.get("sent_fingerprint") == fingerprint:
                # Delivered, and the sheet still says what the applicant was told.
                # An edit taken back before it settled lands here too, and rightly
                # sends nothing.
                continue

            if now - record.get("since", now) < RESULT_QUIET_SECONDS:
                counts["waiting"] += 1
                continue

            awaiting_details = status == "1" and not reason
            # An interview whose details already went out as a message of their
            # own, and the tutor has since edited them — the date has moved, say.
            # Correct it the way it was sent, rather than repeating the invitation.
            details_changed = (
                update
                and status == "1" == record.get("status")
                and bool(record.get("details_sent_at"))
            )

            text_key, counter = STATUS_TEXTS[status]
            if awaiting_details:
                text_key = INTERVIEW_NO_REASON
            elif details_changed:
                text_key = INTERVIEW_DETAILS
            if update:
                counter = "updated"

            # An update writes its note after the earlier one, so column O keeps
            # the whole history of what an applicant was told and when.
            note = f"{row['sent_cell']} " if update else ""

            outcome, detail = await _try_send(
                bot,
                row["telegram_id"],
                await _render(text_key, row["telegram_id"], reason, updated=update),
            )
            if outcome == "flood":
                # Stop this pass; the watcher picks the rest up.
                logger.warning("Telegram asked us to slow down (%ss) — pausing.", detail)
                break
            if outcome == "blocked":
                # Blocked the bot, or never started it — retrying cannot help.
                logger.warning("Cannot reach applicant %s: %s", key, detail)
                record.update(
                    fingerprint=fingerprint,
                    sent_fingerprint=fingerprint,
                    done=True,
                    error=detail,
                )
                state[key] = record
                dirty = True
                counts["failed"] += 1
                stamps.append((row["row_number"], f"{note}❌ yuborilmadi: bot bloklangan"))
                continue
            if outcome == "error":
                attempts = record.get("attempts", 0) + 1
                record.update(fingerprint=fingerprint, attempts=attempts)
                if attempts >= MAX_ATTEMPTS:
                    record.update(sent_fingerprint=fingerprint, done=True, error=detail)
                    counts["failed"] += 1
                    stamps.append(
                        (row["row_number"], f"{note}❌ yuborilmadi: {detail}"[:200])
                    )
                    logger.error(
                        "Giving up on applicant %s after %d attempts: %s",
                        key, attempts, detail,
                    )
                else:
                    logger.warning(
                        "Delivery to applicant %s failed (attempt %d): %s",
                        key, attempts, detail,
                    )
                state[key] = record
                dirty = True
                continue

            record.update(
                fingerprint=fingerprint,
                sent_fingerprint=fingerprint,
                done=True,
                sent_at=now_tashkent().isoformat(timespec="seconds"),
                status=status,
                awaiting_details=awaiting_details,
            )
            record.pop("error", None)
            if awaiting_details:
                # Waiting on a date again, after a tutor took the reason back out.
                # The old follow-up timer must not carry over, or a reason retyped
                # word for word would go out without its quiet period.
                for stale in ("details_fingerprint", "details_since",
                              "details_attempts", "details_sent_at"):
                    record.pop(stale, None)
            state[key] = record
            # Written now rather than at the end of the pass: if the bot dies here,
            # everyone already messaged would otherwise be messaged again on restart.
            dirty = not _persist(state)
            counts[counter] += 1
            if update:
                logger.info(
                    "Application %s changed after its result was sent — the new "
                    "result has gone out.", key,
                )
            mark = f"{note}🔄" if update else "✅"
            stamp = f"{mark} {now_tashkent():%Y-%m-%d %H:%M}"
            if awaiting_details:
                stamp += " (suhbat ma'lumoti kutilmoqda)"
            stamps.append((row["row_number"], stamp))
            await asyncio.sleep(0.05)  # gentle rate limiting

        global _bad_status_seen
        if bad_status - _bad_status_seen:
            logger.warning(
                "Status must be 0, 1 or 2 — nothing will be sent for application(s) %s.",
                ", ".join(sorted(bad_status)),
            )
        _bad_status_seen = bad_status

        # Save locally before touching the sheet: the local record is what prevents
        # a second send, so it must survive even if the sheet write fails.
        if dirty:
            _persist(state)

        if stamps:
            try:
                await asyncio.to_thread(_write_sent_column_sync, sheets_service, stamps)
            except Exception as e:
                logger.error(f"Results were sent but column O could not be updated: {e}")

    delivered = counts["accepted"] + counts["interview"] + counts["rejected"]
    if delivered or counts["details"] or counts["updated"] or counts["failed"]:
        logger.info(
            "Results delivered: %d (accepted %d, interview %d, rejected %d), "
            "interview details %d, updated %d, failed %d, waiting %d, "
            "awaiting details %d, incomplete %d.",
            delivered,
            counts["accepted"],
            counts["interview"],
            counts["rejected"],
            counts["details"],
            counts["updated"],
            counts["failed"],
            counts["waiting"],
            counts["no_details"],
            counts["pending"],
        )
    return counts


async def results_watcher(bot: Bot, interval: int) -> None:
    """Poll the sheet forever, delivering results as tutors finish rows."""
    logger.info(
        "Result watcher started: checking every %ds, sending a row once it has been "
        "unchanged for %ds.",
        interval,
        RESULT_QUIET_SECONDS,
    )
    while True:
        try:
            await asyncio.sleep(interval)
            await deliver_ready_results(bot)
        except asyncio.CancelledError:
            logger.info("Result watcher stopped.")
            raise
        except Exception:
            # Never let one bad pass kill the watcher — the next one may work.
            logger.exception("Result watcher pass failed; will retry.")
