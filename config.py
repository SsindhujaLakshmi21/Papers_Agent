"""
Configuration and Environment Loader for Daily CS Papers Workflow.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Email Settings
GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "").strip()
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "s.sindhu210506@gmail.com").strip()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
USE_TLS = os.getenv("USE_TLS", "True").lower() in ("true", "1", "yes")

# Gemini API Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Pipeline Settings
PAPERS_PER_DAY = int(os.getenv("PAPERS_PER_DAY", "5"))
DB_PATH = DATA_DIR / "papers_history.db"
LOG_FILE = LOGS_DIR / "workflow.log"

# Logging setup
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("CS_Papers_Agent")
