# ExpensesAI Telegram Bot

AI-powered Telegram bot for tracking expenses, income, reports, and basic financial analytics.

## Overview

ExpensesAI is a personal finance Telegram bot built with Python.  
It allows users to track expenses and income, analyze spending, export data, and process receipts using AI.

The project was built as a practical automation system combining Telegram Bot API, SQLite database, and OpenAI API.

## Features

- Add expenses through Telegram messages
- Add income records
- Automatic expense categorization
- AI-powered receipt parsing
- Daily, weekly, and monthly reports
- Spending analytics
- Data export
- SQLite database storage
- Basic error handling

## Tech Stack

- Python
- Telegram Bot API
- OpenAI API
- SQLite
- JSON
- REST API

## Project Structure

Current version:

```text
expensesAI/
├── bot.py
├── requirements.txt
├── README.md
└── .gitignore
```

Planned refactor:

```text
expensesAI/
├── main.py
├── database.py
├── ai.py
├── analytics.py
├── handlers.py
├── config.py
├── requirements.txt
└── README.md
```

## Future Improvements

- Refactor code into modules
- Add button-based Telegram UI
- Add language and currency settings
- Improve analytics
- Add user limits and plans
- Deploy to VPS for 24/7 usage
- Add Docker support

## Author

Built by Rostyslav Ryzhkov  
AI Automation / Python / Telegram Bots