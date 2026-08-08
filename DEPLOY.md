# Deploying the TTPU dormitory bot

The bot long-polls Telegram, so it needs no domain, no TLS certificate, and no open
inbound ports. Any 1 GB VPS is enough.

**Only one instance may run at a time.** Telegram rejects concurrent `getUpdates`
calls for the same token, so a second copy — an old server that comes back, or a
local test run — makes both instances fail with 409 Conflict. Stop the bot locally
before starting it on the server.

## 1. Get the code onto the server

```bash
sudo mkdir -p /opt/ttpu-dor
sudo chown "$USER" /opt/ttpu-dor
git clone <your-repo-url> /opt/ttpu-dor      # or: rsync -av ./ user@server:/opt/ttpu-dor/
```

## 2. Copy the two secret files

`.env` and `credentials.json` are gitignored and will **never** arrive via git. Copy
them from your machine:

```bash
scp .env credentials.json user@server:/tmp/
ssh user@server 'sudo mv /tmp/.env /tmp/credentials.json /opt/ttpu-dor/'
```

`.env` needs six variables: `BOT_TOKEN`, `CHANNEL_ID`, `SPREADSHEET_ID`,
`DRIVE_FOLDER_ID`, `OFERTA_URL`, `ADMIN_IDS`. Four more are optional, all covered
under "Announcing results" below: `RESULT_POLL_SECONDS` (default 120) and
`RESULT_QUIET_SECONDS` (default 600) change result timings, while
`GEMINI_API_KEY`, `GEMINI_MODEL` and `TRANSLATE_REASONS` control translating the
reason into each applicant's language.

## 3. Run the setup script

```bash
sudo bash /opt/ttpu-dor/deploy/setup.sh
```

It installs Python, creates the `ttpu` service account, builds the virtualenv,
locks the secrets to mode 600, and enables + starts the `ttpu-bot` systemd unit.

## 4. Verify

```bash
journalctl -u ttpu-bot -f
```

A healthy start looks like:

```
Synced N previously-recorded applicant(s) from the spreadsheet.
Application ids resume after 286.
Reason translation is on, via gemini-2.0-flash — applicants get the reason in their own language with the tutor's original underneath.
Bot is starting...
Result watcher started: checking every 120s, sending a row once it has been unchanged for 600s.
Run polling for bot @ttpu_dormitory_bot
```

Then send `/start` to [@ttpu_dormitory_bot](https://t.me/ttpu_dormitory_bot) and
confirm the language menu appears.

## Announcing results

Tutors work in three columns of the sheet. Nothing else has to be pressed — the
bot checks every two minutes and messages each applicant on its own.

| Column | Filled by | Meaning |
|---|---|---|
| `M` — Status | tutors | `2` accepted · `1` invited to an interview · `0` not accepted |
| `N` — Reason | tutors | free text the applicant reads word for word. **Required for 2 and 0**, optional for 1 |
| `O` — Sent | the bot | `✅ <date time>` when delivered, or why it could not be |

A row only goes out once M is filled **and** nothing has changed for ten minutes.
That delay is the whole point: tutors type the reason straight into the cell,
Sheets saves every keystroke, and a Telegram message cannot be recalled — so the
bot waits until the wording has stopped moving. Every edit restarts the ten
minutes, so there is no rush to finish a sentence.

### Interviews happen in two steps

Status `1` does not need a reason, because tutors decide who to interview long
before there is a date to give them. A row marked `1` with N empty is sent as
"you are invited, the details will follow", and column O records
`✅ <date time> (suhbat ma'lumoti kutilmoqda)`.

When the date is settled, the tutor writes it into `N` — the date and anything
else the applicant should know, in their own words. After the same ten quiet
minutes the bot delivers that text as a **second, separate message** and appends
`📅 <date time>` to column O. This happens once per row; editing N after those
details have gone out is treated as any other late edit.

Filling M and N together still sends a single message with the reason in it, so
nothing changes for tutors who already know the date.

Apart from that follow-up, each applicant is messaged exactly once. Editing a row
afterwards does **not** re-send it; the bot notes `✏️ keyin tahrirlandi` in column
O and leaves it to a human. To actually send a corrected result, an admin runs
`/resend <application id>`. Blank status means "not reviewed yet" — leaving M
empty never sends a rejection, and anything other than 0/1/2 in M is ignored with
a warning in the log.

Every timestamp the bot writes — column O, the log, its state files — is Tashkent
time (UTC+5), whatever the server's own clock is set to.

Tune the timings with `RESULT_POLL_SECONDS` (default 120) and
`RESULT_QUIET_SECONDS` (default 600) in `.env`.

### Tutors write the reason once, in any language

Applicants read the bot in Uzbek, Russian or English, whichever they picked at
`/start`. The message around the reason has always matched that choice; the
reason in column `N` is a tutor's own words, so the bot machine-translates it to
match and sends **the tutor's exact wording underneath the translation**. Nobody
has to write anything three times, and no applicant is left reading only a
machine's version of why they were turned down.

Tutors write in whatever language suits them. An applicant who chose the same
language sees the text untouched, with no second copy.

The translation runs on the **Gemini API**, which needs one free key and no
credit card:

1. Sign in at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and
   create an API key.
2. Add it to `.env` as `GEMINI_API_KEY=...`.
3. Restart the bot.

> **Do not enable billing on the Google project that key belongs to.** Turning
> billing on deletes that project's Gemini free tier, after which every call bills
> from the first token. This is also why the bot does **not** use Google's Cloud
> Translation API: that one requires a billing account even to spend its free
> allowance.

The free tier allows 15 requests a minute and 1,500 a day, and the bot caches by
text — tutors reuse the same wording across many rows, so a few hundred applicants
usually amount to a few dozen calls. Calls are spaced four seconds apart so a
large first batch cannot burn the per-minute allowance at once. Google has cut
free-tier limits before without notice; if that ever bites, the consequence is
untranslated reasons, never a missed result.

`GEMINI_MODEL` (default `gemini-2.0-flash`) picks the model, should a future one
have better limits.

With no key set — or if the key is rejected, the quota is spent, or the network
fails — the bot logs it once and sends every reason in the tutor's own language,
exactly how it behaved before. Nothing breaks and no result is delayed. To turn
the feature off deliberately, set `TRANSLATE_REASONS=0` in `.env`.

## Local state files

Four JSON files hold state that is **not** in git and **not** in the spreadsheet:

| File | Contents | If lost |
|---|---|---|
| `applied_users.json` | who already applied | rebuilt from sheet column L at startup |
| `app_counter.json` | last issued application id | re-seeded from sheet column A at startup |
| `results_state.json` | who has already been told their result | **applicants may be messaged twice** — see below |
| `user_langs.json` | each applicant's chosen language | **gone for good** — results then go out in Uzbek |

The first two self-heal, which is why a lost server no longer breaks the id
sequence. The other two cannot be rebuilt from the sheet. The language is simply
never written there. `results_state.json` is the record of who has been told their
result: lose it and every decided row is treated as new, so applicants are
messaged a second time. Back both up:

```bash
# On the server — keeps 14 days of copies
sudo tee /etc/cron.daily/ttpu-backup >/dev/null <<'EOF'
#!/bin/sh
mkdir -p /var/backups/ttpu
for f in user_langs results_state; do
  cp /opt/ttpu-dor/$f.json /var/backups/ttpu/$f.$(date +%F).json 2>/dev/null
done
find /var/backups/ttpu -name '*.json' -mtime +14 -delete
EOF
sudo chmod +x /etc/cron.daily/ttpu-backup
```

If `results_state.json` is ever lost without a backup, stop the bot before it
polls again and rebuild it from column O — the sheet is the only other place that
records what was sent.

Copy those backups off the server periodically — a backup that only exists on the
machine you might lose is not a backup.

## Routine operations

```bash
sudo systemctl status ttpu-bot        # is it running?
sudo systemctl restart ttpu-bot       # restart
sudo systemctl stop ttpu-bot          # stop (do this before running it locally)
journalctl -u ttpu-bot -n 100         # recent logs
journalctl -u ttpu-bot -f             # follow live
```

Deploying an update:

```bash
cd /opt/ttpu-dor
sudo -u ttpu git pull
sudo /opt/ttpu-dor/.venv/bin/pip install -r requirements.txt   # only if deps changed
sudo systemctl restart ttpu-bot
```

If the update adds a setting, `.env` will **not** bring it with it — that file is
gitignored and only ever exists on the machine it is on. Edit the server's own
copy before restarting, and keep it mode 600:

```bash
sudo -u ttpu nano /opt/ttpu-dor/.env
sudo systemctl restart ttpu-bot
journalctl -u ttpu-bot -n 30      # confirm the new setting was picked up
```

Restarting drops any updates queued while the bot was down and clears in-progress
application forms — the FSM is in-memory. Prefer restarting at a quiet hour.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `409 Conflict: terminated by other getUpdates` | another instance is polling the same token — find and stop it |
| `BOT_TOKEN is not set!` | `.env` missing from `/opt/ttpu-dor`, or systemd `WorkingDirectory` is wrong |
| `Could not obtain Google Services` | `credentials.json` missing/unreadable, or the service account lost sheet access |
| Rows append but stay unformatted | the service account needs **Editor**, not Viewer, on the spreadsheet |
| Applications get ids that already exist | counter sync failed at startup — check the log for `Failed to read the highest application id` |
| `GEMINI_API_KEY is not set` | no key in `.env` — reasons still go out, in the tutors' own language |
| `Gemini rejected our key` | wrong or revoked key, or billing was enabled on its project (which deletes the free tier) — reasons still go out, untranslated |
