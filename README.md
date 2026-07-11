# ExpensesAI

![CI](https://github.com/rory1337-prog/expense-ai-tg-bot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Alembic](https://img.shields.io/badge/Alembic-enabled-orange)
![Docker](https://img.shields.io/badge/Docker-enabled-2496ED)
![Tests](https://img.shields.io/badge/tests-pytest-green)
![License](https://img.shields.io/badge/license-MIT-success)

Production-ready AI-powered personal finance assistant that automatically extracts expenses from receipt photos, tracks income and spending, and provides intelligent financial analytics through Telegram.

Originally planned as a Make/n8n automation workflow, the project evolved into a fully custom Python backend with a layered architecture, PostgreSQL, SQLAlchemy, Alembic, Docker, and CI/CD.

---

# 🚀 Public Beta

Try the bot:

https://t.me/checkexpenses_ai_bot

---

# Features

- AI receipt recognition using OpenAI Vision
- Structured Outputs (JSON Schema validation)
- Expense & income tracking
- AI-powered financial assistant (`/ask`)
- Daily / Weekly / Monthly reports
- Spending analytics & balance tracking
- Expense editing & deletion
- CSV export
- Multi-language support (EN / RU / PL)
- PostgreSQL persistence
- Docker deployment
- Production VPS hosting

---

# Architecture

```
  Telegram User
        │
        ▼
    aiogram 3
        │
        ▼
 Telegram Handlers
        │
        ▼
 Business Services
        │
        ▼
  Repository Layer
        │
        ▼
  SQLAlchemy ORM
        │
        ▼
   PostgreSQL
```

Receipt processing pipeline:

```
Receipt Photo
      │
      ▼
OpenAI Vision
      │
      ▼
Structured Outputs
 (JSON Schema)
      │
      ▼
  Validation
      │
      ▼
Expense Service
      │
      ▼
  Repository
      │
      ▼
  PostgreSQL
      │
      ▼
Reports & Analytics
```

---

# Tech Stack

## Backend

- Python 3.13
- aiogram 3.x
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- httpx

## AI

- OpenAI Vision
- OpenAI Structured Outputs
- JSON Schema validation

## DevOps

- Docker
- GitHub Actions
- Ubuntu VPS
- Alembic migrations

## Testing

- pytest

---

# Project Structure

```
expense-ai-tg-bot/

├── handlers/
├── services/
├── repositories/
├── db/
│   ├── models.py
│   ├── session.py
│   └── database.py
│
├── ai/
├── analytics/
├── reports/
├── locales/
├── keyboards/
├── states/
├── tests/
│
├── bot.py
├── Dockerfile
├── docker-compose.yml
├── alembic/
└── README.md
```

---

# Key Engineering Features

- Layered architecture
- Repository pattern
- SQLAlchemy ORM
- Alembic database migrations
- PostgreSQL production database
- OpenAI Vision integration
- Structured Outputs validation
- Async HTTP client (httpx)
- Dockerized deployment
- GitHub Actions CI
- Environment-based configuration
- Modular aiogram architecture
- Production-ready error handling

---

# AI Query Examples

Examples of natural language financial analysis:

```
How much did I spend this month?

What is my biggest spending category?

Show my average daily expenses.

How much did I spend on food this week?

Какие у меня самые большие расходы?

Сколько я потратил на транспорт?

Ile wydałem na jedzenie w tym miesiącu?
```

---

# Receipt Processing

The bot automatically:

1. Receives a receipt photo
2. Sends it to OpenAI Vision
3. Extracts structured transaction data
4. Validates JSON output
5. Normalizes expense categories
6. Stores the transaction in PostgreSQL
7. Makes it immediately available for analytics

---

# Testing

Run the test suite:

```bash
pytest
```

Current tests include:

- expense parsing
- income parsing
- category detection
- decimal values
- invalid input handling
- parser validation

---

# Local Development

Clone repository

```bash
git clone https://github.com/rory1337-prog/expense-ai-tg-bot.git
cd expense-ai-tg-bot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure environment

```env
BOT_TOKEN=...
OPENAI_API_KEY=...
DATABASE_URL=postgresql+psycopg://...
```

Run database migrations

```bash
alembic upgrade head
```

Start the bot

```bash
python bot.py
```

Or use Docker

```bash
docker compose up --build
```

---

# Roadmap

### Completed

- AI receipt recognition
- PostgreSQL migration
- SQLAlchemy ORM
- Alembic migrations
- Repository pattern
- Layered architecture
- Docker deployment
- GitHub Actions
- Multi-language support
- Financial analytics

### Planned

- Budget planning
- Smart spending recommendations
- Forecasting
- REST API
- Web dashboard
- Mobile application

---

# Project Evolution

ExpensesAI started as a simple idea:

> "Take a photo of a receipt, automatically save it to the database, and generate monthly expense analysis."

The first implementation was planned as a Make/n8n automation workflow.

As the project evolved, it became a fully custom Python backend with production-grade architecture, AI-powered receipt recognition, relational data modeling, automated database migrations, Docker deployment, and continuous integration.

---

# License

This project is licensed under the MIT License.