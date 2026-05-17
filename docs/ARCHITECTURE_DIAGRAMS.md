# 📊 Email Assistant - Visual Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     EMAIL ASSISTANT                             │
└─────────────────────────────────────────────────────────────────┘

STEP 1: FETCH EMAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  app.py
    │
    ├─► GmailClient (src/clients/gmail_client.py)
    │   └─► Gmail API
    │       └─► list_unprocessed_messages()
    │           └─► get_message()
    │               └─► GmailMessage object
    │                   ├─ subject
    │                   ├─ sender
    │                   ├─ date
    │                   ├─ body_text
    │                   └─ snippet

STEP 2: PROCESS EMAIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                │
                ├─► extract_links() (src/utils/text.py)
                │   └─► URLs from email body
                │
                └─► LLMClient (src/clients/llm_client.py)
                    └─► OpenAI API
                        └─► classify_email()
                            └─► EmailDecision object
                                ├─ action_required (bool)
                                ├─ importance (low/medium/high)
                                ├─ action (str | None)
                                ├─ deadline (str | None)
                                ├─ summary (str)
                                ├─ reason (str)
                                ├─ links (list)
                                └─ should_notify (bool)

STEP 3: STORE RESULT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                │
                └─► Storage (src/clients/storage.py)
                    └─► SQLite Database
                        └─► processed_emails table
                            ├─ gmail_id (PK)
                            ├─ subject
                            ├─ sender
                            ├─ email_date
                            ├─ action_required
                            ├─ importance
                            ├─ action
                            ├─ deadline
                            ├─ summary
                            ├─ reason
                            ├─ links (JSON)
                            ├─ should_notify
                            └─ processed_at

STEP 4: NOTIFY (OPTIONAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                │
                └─ IF should_notify == True
                    │
                    ├─► format_notification() (src/utils/text.py)
                    │   └─► Formatted text
                    │
                    └─► TelegramNotifier (src/clients/telegram.py)
                        └─► Telegram Bot API
                            └─► send_message()
```

## Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    app.py (ORCHESTRATOR)                     │
│                   (at root level)                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
    ┌────────────┐        ┌───────────┐        ┌──────────┐
    │ GmailClient│        │LLMClient  │        │ Storage  │
    │            │        │           │        │          │
    │ src/clients│        │src/clients│        │src/clients
    └────────────┘        └───────────┘        └──────────┘
           │                     │                     │
           ▼                     ▼                     ▼
    ┌────────────┐        ┌───────────┐        ┌──────────┐
    │ Gmail API  │        │OpenAI API │        │SQLite DB │
    └────────────┘        └───────────┘        └──────────┘

    UTILITIES LAYER:
    ┌──────────────────┐  ┌──────────────────┐
    │  src/utils/      │  │ src/models/      │
    │  ├─ prompts.py   │  │ ├─ email.py      │
    │  └─ text.py      │  │ │  - EmailDecision
    │                  │  │  │  - GmailMessage
    └──────────────────┘  └──────────────────┘
```

## Project Structure Tree

```
email_assistant/
│
├── app.py ⭐ MAIN ENTRY POINT
│   Uses: src/config, src/clients/*, src/utils/*
│   Does: Orchestrates email processing workflow
│
├── src/ (PACKAGE)
│   │
│   ├── __init__.py
│   ├── config.py
│   │   ├─ Loads environment variables
│   │   └─ Provides settings object
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── email.py
│   │       ├─ EmailDecision (Pydantic)
│   │       └─ GmailMessage (Data class)
│   │
│   ├── clients/ ⭐ (Storage & Telegram in clients)
│   │   ├── __init__.py
│   │   ├── gmail_client.py
│   │   │   └─ GmailClient: Fetch & parse emails
│   │   ├── llm_client.py
│   │   │   └─ LLMClient: Send to LLM, parse response
│   │   ├── storage.py ⭐
│   │   │   └─ Storage: SQLite database operations
│   │   └── telegram.py ⭐
│   │       └─ TelegramNotifier: Send notifications
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── prompts.py
│   │   │   └─ CLASSIFICATION_PROMPT: LLM system prompt
│   │   └── text.py
│   │       ├─ extract_links()
│   │       └─ format_notification()
│   │
│   └── core/
│       └── __init__.py (ready for business logic)
│
├── scripts/
│   ├── view_db.py
│   │   └─ Database viewer with filters
│   │      python scripts\view_db.py [--limit] [--search] [--notify-only]
│
├── tests/ (ready for unit tests)
│   └── __init__.py
│
├── docs/ (DOCUMENTATION)
│   ├── README.md
│   │   └─ Project overview & quick start
│   ├── SETUP.md
│   │   └─ Windows setup guide
│   └── ARCHITECTURE.md
│       └─ System design & patterns
│
└── config/
    └── .env.example
        └─ Environment variables template
```

## Configuration Flow

```
.env file (local, not in git)
    │
    ├─► Settings (dataclass)
    │   ├─ GMAIL_LABEL
    │   ├─ GMAIL_CREDENTIALS_PATH
    │   ├─ GMAIL_TOKEN_PATH
    │   ├─ OPENAI_API_KEY
    │   ├─ OPENAI_MODEL
    │   ├─ TELEGRAM_BOT_TOKEN
    │   ├─ TELEGRAM_CHAT_ID
    │   └─ SQLITE_PATH
    │
    └─► Used by src/config.py
        └─► Imported in app.py
            └─► Passed to clients
```

## Deployment Readiness

```
DEVELOPMENT
├─ .env (local)
├─ credentials.json (local)
├─ token.json (auto-generated)
└─ assistant.db (auto-created)

PRODUCTION (use .env file)
├─ Environment variables
├─ Credentials from secure storage
├─ Database file or cloud DB
└─ Logging configured
```

## Git Security

```
.gitignore protects:
├─ .env (credentials)
├─ credentials.json (OAuth)
├─ token.json (OAuth token)
├─ *.db (database)
├─ .venv/ (dependencies)
├─ __pycache__/ (Python cache)
└─ .idea/ (IDE files)
```

## Class Diagram

```
EmailDecision (Pydantic Model)
├─ action_required: bool
├─ importance: str
├─ action: str | None
├─ deadline: str | None
├─ summary: str
├─ reason: str
├─ links: list[str]
└─ should_notify: bool

GmailMessage (Data Class)
├─ gmail_id: str
├─ thread_id: str
├─ subject: str
├─ sender: str
├─ date: str
├─ body_text: str
└─ snippet: str

GmailClient
├─ __init__(credentials_path, token_path)
├─ list_unprocessed_messages(label, max_results)
├─ get_message(gmail_id) → GmailMessage
├─ _find_label_id(label_name)
├─ _extract_text(payload)
└─ _decode_base64(data)

LLMClient
├─ __init__(api_key, model)
└─ classify_email(subject, sender, date, body_text) → EmailDecision

Storage
├─ __init__(db_path)
├─ save_email_result(gmail_id, subject, sender, ...)
├─ get_all_processed() → list[dict]
├─ is_processed(gmail_id) → bool
├─ mark_processed(gmail_id, subject)
└─ _init_db()

TelegramNotifier
├─ __init__(bot_token, chat_id)
└─ send_message(text)
```

## Workflow Timeline

```
START
  │
  ├─► 1. GmailClient.list_unprocessed_messages()
  │        │
  │        └─► 2. For each email: GmailClient.get_message()
  │               │
  │               ├─► 3. extract_links()
  │               │
  │               └─► 4. LLMClient.classify_email()
  │                      │
  │                      ├─► 5. Storage.save_email_result()
  │                      │
  │                      └─► 6. IF should_notify:
  │                             │
  │                             └─► 7. TelegramNotifier.send_message()
  │
  └─► END
```

## Environment to Runtime

```
Environment (.env)
    ↓
Load dotenv
    ↓
Settings(dataclass)
    ↓
src/config.py
    ↓
app.py (imports settings)
    ↓
Initialize clients:
├─ GmailClient(settings.gmail_credentials_path, settings.gmail_token_path)
├─ LLMClient(settings.openai_api_key, settings.openai_model)
├─ Storage(settings.sqlite_path)
└─ TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)
    ↓
Run workflow
    ↓
Database & Notifications
```

---

This diagram shows the complete architecture of your refactored email-assistant project!

