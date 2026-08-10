"""Rebuild user_langs.json from the applications channel.

`user_langs.json` is the one piece of applicant state with no second copy: the
sheet stores every choice normalised to Uzbek, so losing the file used to mean
losing every applicant's language for good, and results then went out in Uzbek
to everyone.

The channel turns out to hold the answer. `_caption_args` in utils/preview.py
fills the caption from `faculty_name`, `region_name`, `town_name` and
`reason_name` — the values in the language the applicant picked — while only the
labels are forced to Uzbek. So a post reading

    Yo'nalish: Инженерия кибербезопасности
    Viloyat: Ташкентская область

was written by someone using the bot in Russian, and one reading
"Kompyuter muhandisligi" by someone using Uzbek.

Recovery is therefore an exact lookup, not language guessing: every one of those
values came out of FACULTIES / REGIONS / REASONS in data/regions.py, which hold
all three translations. A value is matched against those tables and the language
it belongs to falls out. Fields whose text is identical in two languages —
"Marketing" is the same in Uzbek and English — simply narrow the answer instead
of deciding it, and the remaining fields settle it.

The bot itself cannot read channel history; the Bot API has no method for it. So
the input is an export made by Telegram Desktop:

    open the channel → ⋮ → Export chat history
      → uncheck photos and files (only the text is needed)
      → format: JSON  → Export

That writes ChatExport_<date>/result.json. Then:

    python tools/recover_langs.py path/to/result.json            # report only
    python tools/recover_langs.py path/to/result.json --write    # write the file

Existing entries in user_langs.json are kept unless --overwrite is given: a
language the applicant chose in the bot is better evidence than one inferred
here.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.regions import FACULTIES, REASONS, REGIONS  # noqa: E402
from texts import t  # noqa: E402

LANGS = ("uz", "ru", "en")

TARGET = Path(__file__).resolve().parent.parent / "user_langs.json"

# The caption labels are always Uzbek, whatever language the values are in, so
# one set of patterns reads every post. The apostrophe is matched loosely: it has
# been typed as ' and ' in different places over the years.
FIELD_PATTERNS = {
    "faculty": re.compile(r"Yo.?nalish:\s*(.+)"),
    "region": re.compile(r"Viloyat:\s*(.+)"),
    "town": re.compile(r"Tuman:\s*(.+)"),
    "reason": re.compile(r"Sabab:\s*(.+?)(?=\n\s*(?:Telefon|Qo.?shimcha|Telegram|User ID):|\Z)", re.S),
}

USER_ID_PATTERN = re.compile(r"User ID:\s*(\d+)")


def _build_tables() -> dict:
    """Map each field to {text seen in a caption: set of languages it could be}."""
    tables = {field: {} for field in ("faculty", "region", "town", "reason")}

    def add(field: str, value: str, lang: str) -> None:
        if value:
            tables[field].setdefault(value.strip(), set()).add(lang)

    for lang in LANGS:
        for faculty in FACULTIES:
            add("faculty", faculty[lang], lang)
        for reason in REASONS:
            add("reason", reason[lang], lang)
        for region in REGIONS:
            add("region", region["name"][lang], lang)
            for town in region["towns"]:
                add("town", town[lang], lang)
        # "Foreign country" is not in the tables — it is a texts.py string, and
        # it stands in for both the region and the town on those applications.
        foreign = t("region_foreign", lang)
        add("region", foreign, lang)
        add("town", foreign, lang)

    return tables


TABLES = _build_tables()


def flatten_text(message: dict) -> str:
    """Recover a message's plain text from a Telegram Desktop export.

    Captions carry bold labels, so the export splits them into runs. Both the
    older "text" list and the newer "text_entities" appear in the wild.
    """
    for key in ("text_entities", "text"):
        value = message.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list):
            parts = [
                part if isinstance(part, str) else str(part.get("text", ""))
                for part in value
            ]
            joined = "".join(parts)
            if joined.strip():
                return joined
    return ""


def detect_language(caption: str) -> tuple:
    """Work out which language an application was filled in.

    Returns (language or None, how it was decided). Each recognised field
    contributes the set of languages its text belongs to; the sets are
    intersected, because one applicant filled every field in one language.
    """
    candidates = []
    for field, pattern in FIELD_PATTERNS.items():
        match = pattern.search(caption)
        if not match:
            continue
        value = match.group(1).strip()
        langs = TABLES[field].get(value)
        if langs:
            candidates.append(langs)

    if not candidates:
        # Every field was free text (a custom town, a written-in reason) or the
        # caption is not an application at all.
        if re.search(r"[Ѐ-ӿ]", caption):
            return "ru", "cyrillic-fallback"
        return None, "no-recognised-field"

    intersection = set(LANGS)
    for langs in candidates:
        intersection &= langs

    if len(intersection) == 1:
        return intersection.pop(), f"exact ({len(candidates)} fields)"

    if not intersection:
        # Contradictory — an applicant who switched language mid-form, or a
        # value that was edited by hand. Fall back to the commonest vote.
        votes = Counter(lang for langs in candidates for lang in langs)
        best, count = votes.most_common(1)[0]
        if count > sum(votes.values()) - count:
            return best, "majority (fields disagree)"
        return None, "contradictory"

    # Still more than one: every matched value happens to be spelled the same in
    # those languages. Cyrillic settles Russian; otherwise leave it undecided.
    if "ru" in intersection and re.search(r"[Ѐ-ӿ]", caption):
        return "ru", "ambiguous + cyrillic"
    if intersection == {"uz", "en"} and not re.search(r"[Ѐ-ӿ]", caption):
        return None, f"ambiguous ({'/'.join(sorted(intersection))})"
    return None, f"ambiguous ({'/'.join(sorted(intersection))})"


def scan(export_path: Path) -> tuple:
    """Read an export and return {user_id: lang} plus a report of how it went."""
    with export_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    messages = payload.get("messages", payload if isinstance(payload, list) else [])

    found: dict = {}
    reasons = Counter()
    undecided: list = []
    seen_applications = 0

    for message in messages:
        caption = flatten_text(message)
        if not caption:
            continue
        id_match = USER_ID_PATTERN.search(caption)
        if not id_match:
            continue  # not an application post
        seen_applications += 1

        user_id = id_match.group(1)
        lang, how = detect_language(caption)
        reasons[how] += 1
        if lang:
            # Later posts win: if somebody applied twice, the newer one is the
            # better record of how they use the bot.
            found[user_id] = lang
        else:
            undecided.append(user_id)

    return found, {
        "applications": seen_applications,
        "how": reasons,
        "undecided": undecided,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("export", type=Path, help="result.json from Telegram Desktop")
    parser.add_argument(
        "--write", action="store_true", help="write user_langs.json (default: report only)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace languages already recorded, instead of keeping them",
    )
    parser.add_argument("--target", type=Path, default=TARGET)
    args = parser.parse_args()

    if not args.export.exists():
        print(f"No such export: {args.export}")
        return 1

    found, report = scan(args.export)

    print(f"Application posts read : {report['applications']}")
    print(f"Languages recovered    : {len(found)}  {dict(Counter(found.values()))}")
    print(f"Undecided              : {len(report['undecided'])}")
    print("\nHow each was decided:")
    for how, count in report["how"].most_common():
        print(f"  {count:5d}  {how}")
    if report["undecided"]:
        sample = ", ".join(report["undecided"][:10])
        print(f"\nUndecided user ids (first 10): {sample}")
        print("These keep the Uzbek default, exactly as before.")

    existing = {}
    if args.target.exists():
        try:
            existing = json.loads(args.target.read_text(encoding="utf-8"))
        except Exception:
            print(f"\n{args.target} is unreadable — it will be replaced.")

    merged = dict(found) if args.overwrite else {**found, **existing}
    kept = len(set(existing) & set(found))
    print(
        f"\nExisting entries: {len(existing)}"
        + (f" ({kept} of them also recovered — "
           + ("overwritten" if args.overwrite else "kept as they are") + ")" if kept else "")
    )
    print(f"Resulting file would hold {len(merged)} entries.")

    if not args.write:
        print("\nReport only. Re-run with --write to save.")
        return 0

    if args.target.exists():
        backup = args.target.with_suffix(".json.bak")
        backup.write_text(args.target.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Previous file copied to {backup.name}")

    args.target.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(merged)} entries to {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
