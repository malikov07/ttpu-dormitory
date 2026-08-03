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

`.env` needs all seven variables: `BOT_TOKEN`, `CHANNEL_ID`, `SPREADSHEET_ID`,
`DRIVE_FOLDER_ID`, `OFERTA_URL`, `ADMIN_IDS`.

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
Run polling for bot @ttpu_dormitory_bot
```

Then send `/start` to [@ttpu_dormitory_bot](https://t.me/ttpu_dormitory_bot) and
confirm the language menu appears.

## Local state files

Three JSON files hold state that is **not** in git and **not** in the spreadsheet:

| File | Contents | If lost |
|---|---|---|
| `applied_users.json` | who already applied | rebuilt from sheet column L at startup |
| `app_counter.json` | last issued application id | re-seeded from sheet column A at startup |
| `user_langs.json` | each applicant's chosen language | **gone for good** — results then go out in Uzbek |

The first two self-heal, which is why a lost server no longer breaks the id
sequence. `user_langs.json` cannot be reconstructed, because the language is never
written to the sheet. Back it up:

```bash
# On the server — keeps 14 days of copies
sudo tee /etc/cron.daily/ttpu-backup >/dev/null <<'EOF'
#!/bin/sh
mkdir -p /var/backups/ttpu
cp /opt/ttpu-dor/user_langs.json /var/backups/ttpu/user_langs.$(date +%F).json 2>/dev/null
find /var/backups/ttpu -name 'user_langs.*.json' -mtime +14 -delete
EOF
sudo chmod +x /etc/cron.daily/ttpu-backup
```

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
