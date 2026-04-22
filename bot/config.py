import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in .env file")

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-r1:8b")
TIMEOUT = int(os.getenv("TIMEOUT", "25"))

# Conversation
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Optional: validate URL format
if not OLLAMA_URL.startswith(("http://", "https://")):
    raise ValueError(f"Invalid OLLAMA_URL: {OLLAMA_URL}")
