# ExpensesAI Telegram Bot
![CI](https://github.com/rory1337-prog/expense-ai-tg-bot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Docker](https://img.shields.io/badge/Docker-enabled-blue)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![Status](https://img.shields.io/badge/status-MVP-success)

AI-powered Telegram bot for personal finance tracking with OpenAI receipt parsing, analytics, reporting, and export functionality.

Built with Python, aiogram, OpenAI API, SQLite, and Docker.

## Features

- AI receipt parsing using OpenAI Vision
- Expense & income tracking
- Multi-language support (EN / RU / PL)
- Daily / weekly / monthly reports
- Analytics & balance tracking
- Edit / delete expense entries
- Export expense history
- Dockerized deployment
- Persistent SQLite storage
- VPS production hosting

## Production Features

- Async OpenAI integration using httpx
- Structured JSON schema validation
- Modular aiogram architecture
- Persistent SQLite database
- Unit-tested parser logic (pytest)
- Unique export file generation
- Environment-based configuration
- Docker restart policies for uptime

## Tech Stack

### Backend

- Python 3
- aiogram 3.x
- SQLite
- OpenAI API
- httpx

### DevOps

- Docker
- Ubuntu VPS
- GitHub
- dotenv

### Testing

- pytest

## Architecture

```text
Telegram User
    ↓
bot.py
    ↓
handlers/
    ↓
parser.py        → text parsing
ai.py            → OpenAI receipt parsing
reports.py       → reports & analytics
database.py      → SQLite operations
    ↓
SQLite
```

## Project Structure

```text
expense-ai-tg-bot/
├── handlers/           # Aiogram routers
├── keyboards/          # Telegram keyboards
├── locales/            # Multi-language texts
├── states/             # FSM states
├── tests/              # Unit tests
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

## Demo

Demo GIF / screenshots coming soon.

## Example Usage

```text
coffee 15
uber 30
/income salary 3000
/report
/today
/week
/month
/balance
/analytics
/export
```

## AI Query Examples

Users can ask natural language finance questions:

- "How much did I spend this month?"
- "What is my top category this week?"
- "How much did I spend on food this month?"
- "Сколько я потратил на транспорт за неделю?"
- "Ile wydałem na groceries w tym miesiącu?"

## Receipt Parsing

1. User sends receipt photo
2. Bot downloads image
3. Image is sent to OpenAI Vision API
4. Structured expense data is extracted
5. Category is normalized locally
6. Data is stored in SQLite

Supported extraction:

* expense name
* amount
* category

## Testing

Run unit tests:

```bash
pytest
```

Current test coverage:

- category detection
- expense parsing
- income parsing
- decimal values
- invalid input handling

## Deployment

Production deployment includes:

- Docker containerization
- Automatic container restart
- `.env`-based secret management
- Persistent SQLite storage
- VPS hosting (Ubuntu)

Run locally:

```bash
git clone https://github.com/rory1337-prog/expense-ai-tg-bot.git
cd expense-ai-tg-bot
pip install -r requirements.txt
python3 bot.py
```

Create `.env`:

```bash
BOTTOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

## Roadmap

- Inline keyboard UI improvements
- PostgreSQL migration
- AI financial assistant (/ask)
- Budget limits & notifications
- Webhook support
- OCR fallback system
- Advanced analytics dashboard
- CI/CD pipeline
- Web/mobile frontend

## Status

Production MVP deployed on VPS with Docker and active development ongoing.

Current focus:

- UX improvements
- AI-powered analytics
- database scalability
- testing & reliability
- infrastructure improvements