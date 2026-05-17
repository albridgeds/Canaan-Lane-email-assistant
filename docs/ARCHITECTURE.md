# Architecture Overview

## Project Structure

The project follows a layered architecture pattern with clear separation of concerns:

```
email_assistant/
├── src/                          # Source code
│   ├── config.py                 # Configuration management
│   │
│   ├── models/
│   │   └── email.py              # Data models
│   │       ├── EmailDecision     # LLM output model
│   │       └── GmailMessage      # Email data model
│   │
│   ├── clients/                  # External service clients
│   │   ├── gmail_client.py       # Gmail API integration
│   │   ├── llm_client.py         # OpenAI API integration
│   │   ├── storage.py            # SQLite database client
│   │   └── telegram.py           # Telegram API integration
│   │
│   ├── utils/                    # Shared utilities
│   │   ├── prompts.py            # LLM system prompts
│   │   └── text.py               # Text processing utilities
│   │
│   └── core/                     # Business logic (future)
│       └── pipeline.py           # Main processing pipeline (TODO)
│
├── scripts/                      # Standalone scripts
│   └── view_db.py                # Database viewer CLI
│
├── tests/                        # Test suite
│   └── __init__.py
│
├── docs/                         # Documentation
│   ├── README.md                 # Project overview
│   ├── SETUP.md                  # Setup instructions
│   └── ARCHITECTURE.md           # This file
│
├── config/                       # Configuration
│   └── .env.example              # Environment template
│
├── app.py                        # Main entry point
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── pyproject.toml                # Project metadata
└── .gitignore                    # Git ignore rules
```

## Layer Description

### 1. Models Layer (`src/models/`)

**Purpose**: Define data structures and schemas

- **`EmailDecision`** (Pydantic model)
  - Represents LLM's analysis of an email
  - Fields: `action_required`, `importance`, `action`, `deadline`, `summary`, `reason`, `links`, `should_notify`
  - Automatically validated by Pydantic

- **`GmailMessage`** (Data class)
  - Represents a parsed Gmail message
  - Fields: `gmail_id`, `thread_id`, `subject`, `sender`, `date`, `body_text`, `snippet`

### 2. Clients Layer (`src/clients/`)

**Purpose**: Handle external service integration

#### `gmail_client.py` - Gmail Integration
- Authenticates with Gmail API
- Fetches messages from specified label
- Extracts and parses email content (text, HTML)
- Methods:
  - `list_unprocessed_messages()` - Get emails from label
  - `get_message()` - Fetch and parse single email

#### `llm_client.py` - LLM Integration
- Communicates with OpenAI API
- Sends emails to LLM for classification
- Parses and validates response
- Methods:
  - `classify_email()` - Analyze email and return `EmailDecision`

#### `storage.py` - Database Integration
- SQLite database operations
- Stores full LLM analysis results
- Methods:
  - `save_email_result()` - Store processed email
  - `get_all_processed()` - Retrieve all records
  - `is_processed()` - Check if email was processed

#### `telegram.py` - Notification Integration
- Sends messages via Telegram Bot API
- Methods:
  - `send_message()` - Send notification

### 3. Utils Layer (`src/utils/`)

**Purpose**: Shared utilities and helper functions

#### `prompts.py`
- Contains LLM system prompt
- Defines expected JSON schema for LLM responses
- Rules for notification logic

#### `text.py`
- `extract_links()` - Extract URLs from text
- `format_notification()` - Format email data for Telegram

### 4. Configuration (`src/config.py`)

**Purpose**: Centralized settings management

- Loads environment variables from `.env`
- Dataclass `Settings` with all configuration
- Default values provided

## Data Flow

```
┌─────────────┐
│ Gmail API   │
└──────┬──────┘
       │
       ├─► GmailClient.list_unprocessed_messages()
       │
       └─► GmailClient.get_message()
           ├─► Parses headers (subject, from, date)
           ├─► Extracts text (plain, HTML, nested parts)
           └─► Returns GmailMessage
               │
               ├─────────────────────────────┐
               │                             │
               ▼                             ▼
         ┌──────────────┐         ┌──────────────────┐
         │ LLMClient    │         │ extract_links()  │
         └──────┬───────┘         └──────────────────┘
                │
                ├─► OpenAI API
                │
                └─► Parses response
                    └─► Returns EmailDecision
                        │
                        ├─► Storage.save_email_result()
                        │   └─► SQLite Database
                        │
                        ├─► format_notification()
                        │
                        └─► TelegramNotifier.send_message()
                            └─► Telegram API
```

## Entry Points

### Main Application (`app.py`)
- Orchestrates the workflow
- Fetches emails → Analyzes with LLM → Stores results → Sends notifications

### Database Viewer (`scripts/view_db.py`)
- Reads from database
- Displays records with filters

## Database Schema

```sql
CREATE TABLE processed_emails (
    gmail_id        TEXT PRIMARY KEY,
    subject         TEXT,
    sender          TEXT,
    email_date      TEXT,
    action_required INTEGER,        -- 0 or 1
    importance      TEXT,           -- "low", "medium", "high"
    action          TEXT,
    deadline        TEXT,
    summary         TEXT,
    reason          TEXT,
    links           TEXT,           -- JSON array as string
    should_notify   INTEGER,        -- 0 or 1
    processed_at    DATETIME        -- AUTO
);
```

## Configuration Management

Environment variables are loaded from `.env`:

```
GMAIL_LABEL              - Gmail label to monitor
GMAIL_CREDENTIALS_PATH   - Path to Gmail OAuth credentials
GMAIL_TOKEN_PATH         - Path to Gmail token
OPENAI_API_KEY           - OpenAI API key
OPENAI_MODEL             - Model to use (e.g., gpt-4-mini)
TELEGRAM_BOT_TOKEN       - Telegram bot token
TELEGRAM_CHAT_ID         - Telegram chat ID
SQLITE_PATH              - Database file path
```

## Design Patterns

### 1. **Layered Architecture**
- Clear separation: Models → Clients → Utils → App
- Easy to test each layer independently

### 2. **Dependency Injection**
- Clients receive configuration in `__init__`
- Makes testing and mocking easier

### 3. **Context Manager** (`@contextmanager`)
- Database connections properly managed
- Automatic commit/rollback

### 4. **Pydantic Models**
- Automatic validation of LLM responses
- Type safety and documentation

## Error Handling

- **Validation Errors**: Caught when parsing LLM response
- **Authentication Errors**: Raised during Gmail/OpenAI auth
- **Database Errors**: Logged but don't stop execution
- **Network Errors**: Request timeouts handled with `timeout` parameter

## Extension Points

### Adding New LLM Provider
1. Create `src/clients/new_llm_client.py`
2. Implement same interface as `llm_client.py`
3. Update `app.py` to use new client

### Adding New Notification Channel
1. Create `src/clients/new_notifier.py`
2. Implement `send_message()` method
3. Update `app.py` to use new notifier

### Adding New Data Source
1. Create `src/clients/new_email_client.py`
2. Return `GmailMessage` objects
3. Update `app.py` to use new client

## Future Improvements

- [ ] Create `src/core/pipeline.py` for main processing logic
- [ ] Add comprehensive test suite in `tests/`
- [ ] Add logging configuration
- [ ] Add database migrations
- [ ] Add CLI commands (click or typer)
- [ ] Add async support
- [ ] Add caching layer

