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
`DRIVE_FOLDER_ID`, `OFERTA_URL`, `ADMIN_IDS`. Two more are optional and only
change result timings: `RESULT_POLL_SECONDS` (default 120) and
`RESULT_QUIET_SECONDS` (default 600) — see "Announcing results" below.

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
| `N` — Reason | tutors | free text, **required**; the applicant reads it word for word |
| `O` — Sent | the bot | `✅ <date time>` when delivered, or why it could not be |

A row only goes out once **both** M and N are filled **and** neither has changed
for ten minutes. That delay is the whole point: tutors type the reason straight
into the cell, Sheets saves every keystroke, and a Telegram message cannot be
recalled — so the bot waits until the wording has stopped moving. Every edit
restarts the ten minutes, so there is no rush to finish a sentence.

Each applicant is messaged exactly once. Editing a row afterwards does **not**
re-send it; the bot notes `✏️ keyin tahrirlandi` in column O and leaves it to a
human. To actually send a corrected result, an admin runs `/resend <application
id>`. Blank status means "not reviewed yet" — leaving M empty never sends a
rejection, and anything other than 0/1/2 in M is ignored with a warning in the log.

Tune the timings with `RESULT_POLL_SECONDS` (default 120) and
`RESULT_QUIET_SECONDS` (default 600) in `.env`.

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
