#!/usr/bin/env bash
# Provision the TTPU dormitory bot on a fresh Ubuntu/Debian VPS.
#
# Run as root on the new server AFTER the code is at /opt/ttpu-dor:
#   sudo bash /opt/ttpu-dor/deploy/setup.sh
#
# Safe to re-run: every step is idempotent.

set -euo pipefail

APP_DIR=/opt/ttpu-dor
APP_USER=ttpu
SERVICE=ttpu-bot

if [[ $EUID -ne 0 ]]; then
    echo "Run this as root: sudo bash $0" >&2
    exit 1
fi

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip

echo "==> Creating service account '$APP_USER'"
# System account: no login shell, no home directory to leak state into.
id -u "$APP_USER" &>/dev/null || useradd --system --shell /usr/sbin/nologin --no-create-home "$APP_USER"

echo "==> Checking for required secret files"
missing=0
for f in .env credentials.json; do
    if [[ ! -f "$APP_DIR/$f" ]]; then
        echo "    MISSING: $APP_DIR/$f" >&2
        missing=1
    fi
done
if [[ $missing -eq 1 ]]; then
    echo "" >&2
    echo "Both files are gitignored, so they are never in the repo. Copy them from" >&2
    echo "your local machine first (see DEPLOY.md step 2), then re-run this script." >&2
    exit 1
fi

echo "==> Building virtualenv"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/requirements.txt"

echo "==> Setting ownership and permissions"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
# Secrets readable only by the service account.
chmod 600 "$APP_DIR/.env" "$APP_DIR/credentials.json"

echo "==> Installing systemd unit"
install -m 644 "$APP_DIR/deploy/$SERVICE.service" "/etc/systemd/system/$SERVICE.service"
systemctl daemon-reload
systemctl enable "$SERVICE"

echo "==> Starting $SERVICE"
systemctl restart "$SERVICE"
sleep 5
systemctl --no-pager --full status "$SERVICE" || true

echo ""
echo "Done. Follow the log with:  journalctl -u $SERVICE -f"
