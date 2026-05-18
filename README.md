# ExpensesAI Telegram Bot

AI-powered Telegram bot for personal expense tracking with receipt parsing, analytics, reports, and data export.

## Features

- Add expenses with simple text messages
- Add income with commands
- Parse receipt photos using OpenAI
- Auto-detect expense categories
- View daily, weekly, and monthly reports
- Track balance, income, and expenses
- Show analytics with top categories and recent expenses
- Export user data as a text file
- Edit and delete saved expenses

## Tech Stack

- Python 3
- Telegram Bot API
- OpenAI API
- SQLite
- dotenv
- requests
- Linux VPS (Ubuntu)
- systemd

## Deployment

The bot is deployed on a Linux VPS (Ubuntu 24.04) and runs 24/7 using a systemd service.

## Project Structure

```text
expensesAI/
├── bot.py              # Main Telegram bot loop and command handlin
├── telegram_api.py     # Telegram API communication
├── ai.py               # OpenAI receipt parsing
├── database.py         # SQLite database operations
├── parser.py           # Text parsing and category detection
├── reports.py          # Reports, analytics, export
├── config.py           # Environment variables and app config
├── requirements.txt
└── README.md
```

## Architecture

```text
Telegram User
    ↓
bot.py
    ↓
telegram_api.py  → Telegram API
    ↓
parser.py        → Text expense/income parsing
ai.py            → Receipt photo parsing with OpenAI
database.py      → SQLite persistence
reports.py       → Reports, analytics, export
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
- timestamp

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

- Docker support
- VPS deployment
- Inline keyboard UI
- PostgreSQL migration
- Unit tests with pytest
- AI financial assistant (`/ask`)
- Budget limits and alerts
- Currency selection
- Multi-user settings

## Status

MVP completed.

Current focus:
- architecture refactoring
- deployment
- testing
- UX improvements
- AI features