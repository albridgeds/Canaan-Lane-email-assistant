# Email Assistant

An intelligent email filtering system that uses LLM to prioritize school emails and send notifications.

## Features

- 📧 **Gmail Integration** - Automatically fetches emails from a specified Gmail label
- 🤖 **LLM Classification** - Uses OpenAI GPT to intelligently analyze emails
- 🔔 **Smart Notifications** - Sends Telegram notifications for important emails
- ⏰ **Daily Deadline Digest** - Sends one daily aggregated reminder for tasks due tomorrow
- 💾 **Full History Storage** - Stores all LLM analysis results in SQLite database
- 📊 **Database Viewer** - CLI tool to view and filter processed emails

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Gmail OAuth credentials
- Telegram bot token (optional)

### Installation

1. **Clone the repository**
   ```powershell
   git clone <repository>
   cd email_assistant
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure** (see [SETUP.md](docs/SETUP.md))
   ```powershell
   copy config\.env.example .env
   copy config\public.env.example config\public.env
   # Edit .env (secrets) and config\public.env (non-secret settings)
   ```

5. **Run**
   ```powershell
   python app.py
   ```

## Usage

### Main Application

Process emails from Gmail and send notifications:

```powershell
python app.py
```

### Daily Deadline Reminder

Send one aggregated reminder for tomorrow deadlines (`should_notify=True`) to both main and debug chats:

```powershell
python scripts\send_deadline_reminders.py
```

**Scheduling:**
- **Linux/Raspberry Pi (systemd)**: See [`systemd_template/README.md`](systemd_template/README.md). Two timers are available:
  - `email-assistant.timer` - runs `app.py` hourly (Mon–Fri 9:00–18:00)
  - `email-assistant-reminders.timer` - runs `send_deadline_reminders.py` daily at 19:00

- **Windows (Task Scheduler)**: See [`docs/SETUP.md`](docs/SETUP.md) for `schtasks` example.

### View Database

View all processed emails:

```powershell
# Show all records
python scripts\view_db.py

# Show last 10 records
python scripts\view_db.py --limit 10

# Search by subject
python scripts\view_db.py --search "homework"

# Show only notifications
python scripts\view_db.py --notify-only
```

## Project Structure

```
email_assistant/
├── src/                          # Main source code
│   ├── config.py                 # Configuration management
│   ├── models/
│   │   └── email.py              # Data models (EmailDecision, GmailMessage)
│   ├── clients/
│   │   ├── gmail_client.py       # Gmail API client
│   │   ├── llm_client.py         # OpenAI LLM client
│   │   ├── storage.py            # SQLite database client
│   │   └── telegram.py           # Telegram notification client
│   └── utils/
│       ├── prompts.py            # LLM system prompts
│       └── text.py               # Text processing utilities
├── scripts/
│   ├── send_deadline_reminders.py # Daily deadline digest sender
│   └── view_db.py                # Database viewer CLI
├── docs/
│   ├── SETUP.md                  # Detailed setup instructions
│   └── README.md                 # This file
├── config/
│   └── .env.example              # Environment template
├── app.py                        # Main entry point
├── requirements.txt              # Dependencies
└── .gitignore                    # Git ignore rules
```

## Configuration

Configuration is split into two files:

- `.env` - protected secrets only (`TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`)
- `config/public.env` - non-secret runtime settings

```env
# .env (secrets)
TELEGRAM_BOT_TOKEN=your_token
OPENAI_API_KEY=your_key
```

```env
# config/public.env (non-secrets)
GMAIL_LABEL=School
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_DEBUG_CHAT_ID=your_private_chat_id
OPENAI_MODEL=gpt-4.1-mini
SQLITE_PATH=assistant.db
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
NOTIFICATION_MODE=all
DEBUG_NOTIFICATION_MODE=important_only
```

See `config/.env.example` and `config/public.env.example` for templates.

## How It Works

1. **Fetch** - Retrieves unread emails from specified Gmail label
2. **Analyze** - Sends to OpenAI for intelligent classification
3. **Store** - Saves full LLM output to SQLite database
4. **Notify** - Sends Telegram message for important emails
5. **Remind** - Sends daily aggregated deadline digest for tomorrow tasks
6. **View** - Access history via CLI viewer

## Database Schema

The `processed_emails` table stores:
- `gmail_id` - Gmail message ID
- `subject`, `sender`, `email_date` - Email metadata
- `action_required`, `importance` - LLM analysis
- `action`, `deadline` - Extracted information
- `summary`, `reason` - LLM explanation
- `links` - Extracted URLs
- `should_notify` - Notification flag
- `processed_at` - Processing timestamp

## Troubleshooting

### Import Errors
Make sure you're running from project root with virtual environment activated.

### Gmail Auth Fails
First run will open browser for OAuth. Click "Allow" to authorize.

### LLM Parsing Error
Check that `OPENAI_API_KEY` is valid and account has sufficient credits.

## Development

### Running Tests
```powershell
pytest
```

### Code Style
This project uses standard Python conventions.

## Contributing

Contributions welcome! Please:
1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

