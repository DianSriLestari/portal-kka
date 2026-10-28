import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
SLIDES_DIR = UPLOADS_DIR / "slides"

# Ensure data, static, and uploads directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "images").mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
SLIDES_DIR.mkdir(parents=True, exist_ok=True)

# Database file path
DB_PATH = DATA_DIR / "kka_learning.db"

# Security & Sessions
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-kka-key-sma7-2026")
COOKIE_NAME = "kka_session_token"
SESSION_EXPIRE_HOURS = 24
