# ExpensesAI Telegram Bot

AI-powered Telegram bot for personal expense tracking with receipt parsing, analytics, reports, and data export.

GitHub repository: https://github.com/rory1337-prog/expense-ai-tg-bot

## Features

- AI receipt parsing (OpenAI Vision)
- Expense & income tracking
- Multilanguage support (EN / RU / PL)
- Reports & analytics
- Edit / delete entries
- Export data
- Docker deployment
- VPS 24/7 hosting
- SQLite storage

## Tech Stack

- Python 3
- Telegram Bot API
- OpenAI API
- SQLite
- dotenv
- requests
- Docker
- Linux VPS (Ubuntu)

## Deployment

The bot is deployed on an Ubuntu VPS and containerized using Docker.

Production setup includes:
- Docker containerization
- automatic Docker container restart
- environment variable management with `.env`
- persistent SQLite storage
- GitHub-based deployment workflow

## Project Structure

```text
expense-ai-tg-bot/
├── handlers/           # Aiogram routers
├── keyboards/          # Telegram keyboards
├── locales/            # Multilanguage texts
├── states/             # FSM states
├── ai.py               # OpenAI receipt parsing
├── parser.py           # Expense/income parsing
├── reports.py          # Reports & analytics
├── database.py         # SQLite operations
├── config.py           # Environment config
├── bot.py              # Bot entrypoint
├── Dockerfile
├── requirements.txt
└── README.md
```

## Architecture


```text
Telegram User
    ↓
bot.py                      # aiogram entrypoint
    ↓
handlers/                   # routers & message handlers
    ↓
parser.py                   # text expense/income parsing
ai.py                       # OpenAI receipt parsing
reports.py                  # reports & analytics
database.py                 # SQLite persistence
    ↓
SQLite
```

## Example Usage

```text
coffee 15
burger king 25
/income salary 3000
/report
/today
/week
/month
/balance
/analytics
/export
```

## Receipt Parsing

Users can send a receipt photo directly in Telegram.  
The bot downloads the image, sends it to OpenAI, extracts structured expense data, normalizes the category, and stores everything in SQLite.

Supported extraction:
- expense name
- amount
- category

## Setup

1. Clone repository:

```bash
git clone https://github.com/rory1337-prog/expense-ai-tg-bot.git
cd expense-ai-tg-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file:

```env
BOTTOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

4. Run the bot:

```bash
python3 bot.py
```

## Roadmap

- Inline keyboard UI
- PostgreSQL migration
- Unit tests with pytest
- AI financial assistant (`/ask`)
- Budget limits and alerts
- Currency selection
- Multi-user settings
- Webhook-based deployment

## Status

Production MVP deployed.

Current focus:
- command handler architecture
- UX improvements
- testing
- AI features
- database scalability