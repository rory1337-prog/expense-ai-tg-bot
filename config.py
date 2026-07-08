# ===== IMPORTS =====
import os
from pathlib import Path
from dotenv import load_dotenv

# ===== ENVIRONMENT =====
load_dotenv(
    dotenv_path=Path(__file__).with_name(".env"),
    override=False
)

BOT_TOKEN = os.getenv("BOTTOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOTTOKEN is missing in .env")

# ===== PATHS =====
BASE_DIR = Path(__file__).parent
DB_FILE = os.getenv("DB_FILE", "expenses.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")
UPDATE_FILE = BASE_DIR / "update.txt"

# ===== APP SETTINGS =====
CURRENCY = "PLN"

# ===== TELEGRAM =====
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
TELEGRAM_DOCUMENT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"