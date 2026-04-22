# bot/main.py - Main entry point for Tux Chat Telegram Bot.

import logging

from telegram.ext import Application

from bot.ai.ollama_text import OllamaTextClient
from bot.config import DEFAULT_MODEL, LOG_LEVEL, TELEGRAM_TOKEN
from bot.dispatcher import register_handlers
from bot.memory.session import SessionManager

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Called after the application is initialized."""
    logger.info("Bot started and ready to receive messages")


async def shutdown(application: Application):
    """Cleanup on shutdown."""
    logger.info("Shutting down, closing AI client...")
    ai_client = application.bot_data.get("ai_client")
    if ai_client:
        await ai_client.close()
    logger.info("Shutdown complete")


def main():
    """Start the bot."""
    # Asegurar que el token no es None (config.py ya lo valida, pero esto ayuda al type checker)
    assert TELEGRAM_TOKEN is not None, "TELEGRAM_TOKEN is not configured"

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Initialize shared resources
    ai_client = OllamaTextClient()
    session_manager = SessionManager()

    # Store in bot_data (shared across all handlers)
    application.bot_data["ai_client"] = ai_client
    application.bot_data["session_manager"] = session_manager
    application.bot_data["current_model"] = DEFAULT_MODEL

    # Register handlers
    register_handlers(application)

    # Setup lifecycle events
    application.post_init = post_init
    application.post_shutdown = shutdown

    # Start polling
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
