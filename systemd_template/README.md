# systemd template (Raspberry Pi)

This folder contains `systemd` unit templates for running `email_assistant` on Raspberry Pi as a scheduled task.

Files:
- `email-assistant.service` - one-shot run of `app.py`
- `email-assistant.timer` - periodic schedule for the service
- `install.sh` - helper installer script
- `update.sh` - manual update script (sync from GitHub `main` + reload units)

Before install:
1. Update `User`, `WorkingDirectory`, and `ExecStart` in `email-assistant.service`.
2. Make sure the virtual environment and dependencies are installed.
3. Ensure runtime files/config are available on the server (for example: `credentials.json`, `token.json`, and environment variables if required).

Install:
```bash
cd /home/pi/email_assistant/systemd_template
chmod +x install.sh
sudo ./install.sh
```

Check status and logs:
```bash
systemctl status email-assistant.service --no-pager
systemctl status email-assistant.timer --no-pager
systemctl list-timers --all | grep email-assistant
journalctl -u email-assistant.service -n 100 --no-pager
```

Reload after file updates:
```bash
# If only app code/config changed:
sudo systemctl restart email-assistant.timer

# If .service/.timer files changed in /etc/systemd/system:
sudo systemctl daemon-reload
sudo systemctl restart email-assistant.timer

# Optional: run job immediately to verify
sudo systemctl start email-assistant.service
```

Manual update on Raspberry Pi:
```bash
cd /home/pi/email_assistant/systemd_template
chmod +x update.sh
./update.sh
```

What `update.sh` does:
- fetches and hard-resets local repo to `origin/main`
- installs Python dependencies from `requirements.txt` using `venv`/`.venv` if present
- installs current unit files into `/etc/systemd/system`
- runs `systemctl daemon-reload`, restarts timer, and restarts service once

Disable/remove:
```bash
sudo systemctl disable --now email-assistant.timer
sudo systemctl disable --now email-assistant.service || true
sudo rm -f /etc/systemd/system/email-assistant.service /etc/systemd/system/email-assistant.timer
sudo systemctl daemon-reload
```
