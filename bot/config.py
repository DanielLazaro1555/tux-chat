# config.py - Configuration file for the Tux Chat bot

import os

from dotenv import load_dotenv

# Importar el cargador de prompts (después de crear la estructura)
from bot.prompts.loader import load_prompt

# Load .env file
load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in .env file")

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "TUX IA Secreta Privada")
TIMEOUT = int(os.getenv("TIMEOUT", "25"))

# Conversation
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Optional: validate URL format
if not OLLAMA_URL.startswith(("http://", "https://")):
    raise ValueError(f"Invalid OLLAMA_URL: {OLLAMA_URL}")

# Max tokens for generation (approx 4 chars/token -> ~6000 chars, safe for Telegram)
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1500"))

# System prompt: nombre del prompt a usar (por defecto "default")
SYSTEM_PROMPT_NAME = os.getenv("SYSTEM_PROMPT_NAME", "default")

# Cargar el texto del prompt desde el archivo correspondiente
SYSTEM_PROMPT_TEXT = load_prompt(SYSTEM_PROMPT_NAME)
