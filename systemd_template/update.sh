#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="email-assistant.service"
TIMER_NAME="email-assistant.timer"
REMOTE_NAME="origin"
BRANCH_NAME="main"
SYSTEMD_DIR="/etc/systemd/system"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

run_root() {
  if [[ "${EUID}" -eq 0 ]]; then
    "$@"
  else
    sudo "$@"
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command not found: $1" >&2
    exit 1
  }
}

require_cmd git
require_cmd systemctl
require_cmd install

if [[ "${EUID}" -ne 0 ]]; then
  require_cmd sudo
fi

echo "Repository: ${REPO_DIR}"
cd "${REPO_DIR}"

if [[ ! -d .git ]]; then
  echo "Not a git repository: ${REPO_DIR}" >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Warning: local git changes will be discarded by reset --hard."
fi

echo "Syncing with ${REMOTE_NAME}/${BRANCH_NAME}..."
git fetch --prune "${REMOTE_NAME}"
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
  git checkout "${BRANCH_NAME}"
else
  git checkout -B "${BRANCH_NAME}" "${REMOTE_NAME}/${BRANCH_NAME}"
fi
git reset --hard "${REMOTE_NAME}/${BRANCH_NAME}"

echo "Updating Python dependencies..."
if [[ -x "${REPO_DIR}/venv/bin/python" ]]; then
  PYTHON_BIN="${REPO_DIR}/venv/bin/python"
elif [[ -x "${REPO_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${REPO_DIR}/.venv/bin/python"
else
  PYTHON_BIN=""
fi

if [[ -n "${PYTHON_BIN}" ]]; then
  "${PYTHON_BIN}" -m pip install -r "${REPO_DIR}/requirements.txt"
else
  echo "Warning: no venv python found at venv/bin/python or .venv/bin/python. Skipping dependency install."
fi

echo "Installing/refreshing systemd units..."
run_root install -m 0644 "${REPO_DIR}/systemd_template/${SERVICE_NAME}" "${SYSTEMD_DIR}/${SERVICE_NAME}"
run_root install -m 0644 "${REPO_DIR}/systemd_template/${TIMER_NAME}" "${SYSTEMD_DIR}/${TIMER_NAME}"

run_root systemctl daemon-reload
run_root systemctl restart "${TIMER_NAME}"
# oneshot service: restart triggers an immediate run with updated code
run_root systemctl restart "${SERVICE_NAME}"

echo
run_root systemctl status "${SERVICE_NAME}" --no-pager || true
run_root systemctl status "${TIMER_NAME}" --no-pager || true

echo
run_root systemctl list-timers --all | grep "email-assistant" || true

echo "Update complete."

