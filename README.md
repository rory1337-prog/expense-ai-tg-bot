# 💸 ExpensesAI 

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

![Pytest](https://img.shields.io/badge/Tests-52%20Passing-success?style=for-the-badge)
![mypy](https://img.shields.io/badge/mypy-Passing-blue?style=for-the-badge)
![Ruff](https://img.shields.io/badge/Ruff-Passing-black?style=for-the-badge)
![Black](https://img.shields.io/badge/Black-Code%20Style-000000?style=for-the-badge)

> 🚀 **Stable Release v1.0.0**
>
>AI-powered Telegram bot for tracking expenses from receipts with natural-language spending analytics.

**Try it** [@checkexpenses_ai_bot](https://t.me/checkexpenses_ai_bot)

![Demo](assets/demo.gif)

## Features

* 📸 Receipt recognition via OpenAI Vision and Structured Outputs
* 💸 Expense and income tracking
* 💰 Balance, edit/delete, and CSV export
* 📊 Daily, weekly, and monthly reports
* 🤖 `/ask` analytics: total spending, daily average, category spending, top category, and biggest expenses
* 🌍 English / Русский / Polski
* 💱 Configurable currencies and timezone-aware reporting

## How it works

```
Telegram → handlers → services → repositories → SQLAlchemy → PostgreSQL
Receipt → OpenAI Vision → structured JSON → validation → database
```

Database migrations are managed with Alembic. Dates are stored in UTC and reporting periods are calculated in the configured application timezone.

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend  | Python 3.13, aiogram 3, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Alembic |
| AI       | OpenAI Vision, Structured Outputs, GPT-4.1-mini |
| DevOps   | Docker, GitHub Actions, Ubuntu VPS |
| Quality  | Ruff, Black, mypy, pytest |

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

### v1.1

- Budget management
- Budget alerts
- Monthly comparison
- Charts

### v1.2

- FastAPI REST API
- Redis
- Celery

### v2.0

- Web Dashboard
- Multi-user API
- OCR Pipeline improvements

## License

[MIT](LICENSE)