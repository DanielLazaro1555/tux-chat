# bot/dispatcher.py - Dispatcher to route Telegram updates to appropriate handlers.

from telegram.ext import CommandHandler, MessageHandler, filters

from bot.handlers import commands, document, text  # <-- AÑADIR document


def register_handlers(application):
    """Register all command and message handlers."""
    # Command handlers
    application.add_handler(CommandHandler("start", commands.start))
    application.add_handler(CommandHandler("reset", commands.reset))
    application.add_handler(CommandHandler("models", commands.list_models))
    application.add_handler(CommandHandler("model", commands.change_model))
    application.add_handler(CommandHandler("help", commands.help_command))

    # Message handler (text only, not commands)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text.handle_text)
    )

    # Document handler (PDF, DOCX, TXT)
    application.add_handler(
        MessageHandler(filters.Document.ALL, document.handle_document)
    )
