# ExpensesAI

![CI](https://github.com/rory1337-prog/expense-ai-tg-bot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![License](https://img.shields.io/badge/license-MIT-green)

AI-powered Telegram finance assistant: send a receipt photo, track expenses and income, generate reports, and ask questions about your finances in natural language.

**Try it** [@checkexpenses_ai_bot](https://t.me/checkexpenses_ai_bot)

![Demo](assets/demo.gif)

## Features

* 📸 Receipt recognition via OpenAI Vision and Structured Outputs
* 💸 Expense and income tracking
* 💰 Balance, edit/delete, and CSV export
* 📊 Daily, weekly, and monthly reports
* 🤖 `/ask` analytics: total spending, daily average, category spending, top category, and biggest expenses
* 🌍 English / Русский / Polski
* 💱 Currency settings and timezone-aware reporting

## How it works

```
Telegram → handlers → services → repositories → SQLAlchemy → PostgreSQL
Receipt → OpenAI Vision → structured JSON → validation → database
```

Database migrations are managed with Alembic. Dates are stored in UTC and reporting periods are calculated in the configured application timezone.

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend  | Python 3.13, aiogram, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic |
| AI       | OpenAI Vision, Structured Outputs |
| DevOps   | Docker, GitHub Actions, Ubuntu VPS |
| Quality  | Ruff, Black, mypy, pytest, pre-commit |

## Quick Start

```bash
git clone https://github.com/rory1337-prog/expense-ai-tg-bot.git
cd expense-ai-tg-bot
cp .env.example .env
docker compose up --build
```

| Variable | Description |
|----------|-------------|
| `BOTTOKEN` | Telegram bot token |
| `OPENAI_API_KEY` | OpenAI API key |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `APP_TIMEZONE` | Reporting timezone, for example Europe/Warsaw |

Docker Compose generates `DATABASE_URL` automatically. When running without Docker, provide it manually and run `alembic upgrade head` before `python bot.py`.

## Development

```bash
ruff check .
black --check .
mypy config.py db repositories services
pytest -q
```

CI runs the checks against PostgreSQL 16, applies Alembic migrations, runs the test suite, and builds the Docker image.

## Roadmap

* [x] AI receipt parsing, financial analytics, PostgreSQL, Docker, CI
* [ ] Budgets and threshold alerts
* [ ] Monthly comparisons and Telegram charts
* [ ] Scheduled reports
* [ ] REST API and web dashboard

## License

[MIT](LICENSE)