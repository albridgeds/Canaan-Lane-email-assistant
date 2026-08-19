#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="email-assistant.service"
TIMER_NAME="email-assistant.timer"
SERVICE_REMINDERS_NAME="email-assistant-reminders.service"
TIMER_REMINDERS_NAME="email-assistant-reminders.timer"
DEST_DIR="/etc/systemd/system"
TEMPLATE_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo ./install.sh"
  exit 1
fi

echo "Installing systemd units to ${DEST_DIR}"
install -m 0644 "${TEMPLATE_DIR}/${SERVICE_NAME}" "${DEST_DIR}/${SERVICE_NAME}"
install -m 0644 "${TEMPLATE_DIR}/${TIMER_NAME}" "${DEST_DIR}/${TIMER_NAME}"
install -m 0644 "${TEMPLATE_DIR}/${SERVICE_REMINDERS_NAME}" "${DEST_DIR}/${SERVICE_REMINDERS_NAME}"
install -m 0644 "${TEMPLATE_DIR}/${TIMER_REMINDERS_NAME}" "${DEST_DIR}/${TIMER_REMINDERS_NAME}"

systemctl daemon-reload

# Timer controls periodic oneshot runs of the service.
systemctl enable --now "${TIMER_NAME}"
systemctl enable --now "${TIMER_REMINDERS_NAME}"

echo
echo "Done. Status:"
systemctl status "${SERVICE_NAME}" --no-pager || true
systemctl status "${TIMER_NAME}" --no-pager || true
systemctl status "${SERVICE_REMINDERS_NAME}" --no-pager || true
systemctl status "${TIMER_REMINDERS_NAME}" --no-pager || true

echo
echo "Next runs:"
systemctl list-timers --all | grep "email-assistant" || true
