"""Send a day's applicants their interview details again.

For the case where the invitations are known to have gone out but somebody wants
them said twice — a channel link nobody joined, a delivery log that lost its
stamps, an interview a few hours away. It reads a dated tab, takes the text the
tutors wrote in column N, and sends each applicant the same message the results
watcher sends, in their own language.

    python tools/resend_details.py 13.08              # dry run, sends nothing
    python tools/resend_details.py 13.08 --send
    python tools/resend_details.py 13.08 --send --no-reminder

Run it on the server. The applicant's language lives in `user_langs.json` and the
reason is translated with `GEMINI_API_KEY`, both of which only exist there — run
from anywhere else and applicants who chose Russian or English get an Uzbek
reason, unlike the message they already hold.

`results_state.json` is deliberately left alone. The watcher already has these
rows recorded as delivered and their fingerprints match the sheet, so it will not
send anything of its own accord; touching the record here is what would cause a
third message rather than prevent one.

Safe to run while the bot is running: only `getUpdates` may not be shared, and
this sends.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiogram import Bot

from config import BOT_TOKEN, SPREADSHEET_ID, now_tashkent
from utils.google_api import get_services
from utils.lang_store import get_user_lang
from utils.results import INTERVIEW_DETAILS, _render, _try_send

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

COL_ID, COL_NAME, COL_TGID, COL_REASON = 0, 1, 11, 13

# Sent on top of the message. An applicant who reads the same invitation twice
# with nothing to explain it reasonably wonders whether the first one still holds.
REMINDER = {
    "uz": "🔔 <b>Eslatma</b> — bu xabar sizga avval ham yuborilgan edi.\n\n",
    "ru": "🔔 <b>Напоминание</b> — это сообщение уже отправлялось вам ранее.\n\n",
    "en": "🔔 <b>Reminder</b> — this message was sent to you earlier as well.\n\n",
}


def cell(row: list, index: int) -> str:
    if len(row) <= index:
        return ""
    value = row[index]
    return value.strip() if isinstance(value, str) else str(value).strip()


def read_tab(tab: str) -> list:
    """Applicants on a dated tab who have both a Telegram id and a reason."""
    service = get_services()
    if service is None:
        sys.exit("Could not reach Google Sheets — check credentials.json.")
    values = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"'{tab}'!A1:N")
        .execute()
        .get("values", [])
    )
    rows = []
    for raw in values:
        try:
            telegram_id = int(float(cell(raw, COL_TGID)))
        except (ValueError, TypeError):
            continue  # header row, or a row the bot did not write
        reason = cell(raw, COL_REASON)
        if not reason:
            continue  # nothing to tell them
        rows.append(
            {
                "app_id": cell(raw, COL_ID),
                "name": cell(raw, COL_NAME),
                "telegram_id": telegram_id,
                "reason": reason,
            }
        )
    return rows


async def send_one(bot: Bot, row: dict, reminder: bool, force_lang=None) -> tuple:
    """One applicant, retrying once if Telegram asks us to slow down."""
    lang = force_lang or get_user_lang(row["telegram_id"])
    text = await _render(
        INTERVIEW_DETAILS, row["telegram_id"], row["reason"], lang=lang
    )
    if reminder:
        text = REMINDER.get(lang, REMINDER["uz"]) + text

    outcome, detail = await _try_send(bot, row["telegram_id"], text)
    if outcome == "flood":
        try:
            wait = int(float(detail)) + 1
        except (ValueError, TypeError):
            wait = 5
        print(f"      Telegram asked for {wait}s — waiting")
        await asyncio.sleep(wait)
        outcome, detail = await _try_send(bot, row["telegram_id"], text)
    return outcome, detail, lang


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a day's applicants their interview details again."
    )
    parser.add_argument(
        "tab", nargs="?", default=now_tashkent().strftime("%d.%m"),
        help="dated tab to read (default: today, e.g. 13.08)",
    )
    parser.add_argument(
        "--send", action="store_true",
        help="actually send; without it nothing leaves the machine",
    )
    parser.add_argument(
        "--no-reminder", action="store_true",
        help="send the message verbatim, with no 'you have had this before' line",
    )
    parser.add_argument(
        "--lang", choices=("uz", "en", "ru"),
        help="write to everyone in this language instead of each applicant's own; "
             "the tutors' original wording still travels underneath",
    )
    parser.add_argument("--pause", type=float, default=0.15,
                        help="seconds between messages (default 0.15)")
    args = parser.parse_args()

    rows = read_tab(args.tab)
    if not rows:
        sys.exit(f"No applicants with a reason on tab {args.tab!r}.")

    print(f"Tab {args.tab}: {len(rows)} applicant(s) with something to tell them.")
    print(f"Language: {args.lang or 'each applicant’s own'}\n")
    print(f"The text in column N:\n  {rows[0]['reason']}\n")

    if not args.send:
        # Render one message in full, so what is about to go out can be read
        # before it does rather than after.
        preview = await _render(
            INTERVIEW_DETAILS, rows[0]["telegram_id"], rows[0]["reason"],
            lang=args.lang or get_user_lang(rows[0]["telegram_id"]),
        )
        if not args.no_reminder:
            lang = args.lang or get_user_lang(rows[0]["telegram_id"])
            preview = REMINDER.get(lang, REMINDER["uz"]) + preview
        print("Each applicant receives:\n")
        print("\n".join("  " + line for line in preview.splitlines()))
        print()
        for r in rows:
            print(f"  {r['app_id']:>5}  {r['telegram_id']:>12}  "
                  f"{args.lang or get_user_lang(r['telegram_id'])}  {r['name']}")
        print("\nDry run — nothing sent. Re-run with --send.")
        return

    bot = Bot(token=BOT_TOKEN)
    sent = blocked = failed = 0
    try:
        for i, row in enumerate(rows, 1):
            outcome, detail, lang = await send_one(
                bot, row, not args.no_reminder, args.lang
            )
            if outcome == "sent":
                sent += 1
                mark = "ok"
            elif outcome == "blocked":
                blocked += 1
                mark = f"BLOCKED — {detail[:60]}"
            else:
                failed += 1
                mark = f"FAILED — {detail[:60]}"
            print(f"  {i:>3}/{len(rows)}  {row['app_id']:>5}  {lang}  "
                  f"{row['name'][:32]:<32} {mark}")
            await asyncio.sleep(args.pause)
    finally:
        await bot.session.close()

    print(f"\n  sent     {sent:>4}")
    print(f"  blocked  {blocked:>4}  (bot blocked or never started — unreachable)")
    print(f"  failed   {failed:>4}")
    print("\nresults_state.json untouched — the watcher will not send these again.")


if __name__ == "__main__":
    asyncio.run(main())
