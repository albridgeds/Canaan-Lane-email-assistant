# Setup Instructions for Windows

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation Steps

### 1. Clone or Download the Project

```powershell
cd path\to\projects
git clone <repository-url>
cd email_assistant
```

### 2. Create Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate Virtual Environment

```powershell
# For PowerShell:
.venv\Scripts\Activate.ps1

# For Command Prompt (cmd.exe):
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure Gmail OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 Desktop Application credentials
5. Download credentials as JSON file
6. Save as `credentials.json` in project root

### 6. Configure Environment Variables

1. Copy the example configuration:
   ```powershell
   copy config\.env.example .env
   copy config\public.env.example config\public.env
   ```

2. Edit `.env` file with secrets only:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   OPENAI_API_KEY=your_key_here
   ```

3. Edit `config/public.env` with non-secret settings:
   ```
   GMAIL_LABEL=School
   TELEGRAM_CHAT_ID=your_chat_id_here
   OPENAI_MODEL=gpt-4.1-mini
   SQLITE_PATH=assistant.db
   GMAIL_CREDENTIALS_PATH=credentials.json
   GMAIL_TOKEN_PATH=token.json
   NOTIFICATION_MODE=all
   ```

## Running the Application

### Main Application

```powershell
# From project root, with venv activated:
python app.py
```

### View Database Records

```powershell
python scripts\view_db.py
python scripts\view_db.py --limit 5
python scripts\view_db.py --search "homework"
python scripts\view_db.py --notify-only
```

## Troubleshooting

### Import Errors

If you get import errors, make sure:
1. Virtual environment is activated
2. You're running from the project root directory
3. All dependencies are installed: `pip install -r requirements.txt`

### Gmail Authentication

On first run, a browser window will open asking for Gmail permissions. Click "Allow" to authorize.

### Database Issues

If you get database errors:
1. Delete `assistant.db` to reset
2. The database will be recreated on next run

## Project Structure

```
email_assistant/
├── src/                          # Source code
│   ├── config.py                 # Configuration
│   ├── models/email.py           # Data models
│   ├── clients/
│   │   ├── gmail_client.py       # Gmail integration
│   │   ├── llm_client.py         # OpenAI integration
│   │   ├── storage.py            # Database
│   │   └── telegram.py           # Telegram notifier
│   └── utils/
│       ├── prompts.py            # LLM prompts
│       └── text.py               # Text utilities
├── scripts/
│   └── view_db.py                # Database viewer
├── app.py                        # Main application
├── requirements.txt              # Dependencies
├── .env                          # Secrets only (create from config/.env.example)
└── config/
    ├── .env.example              # Secrets template
    ├── public.env                # Non-secret settings
    └── public.env.example        # Non-secret template
```

