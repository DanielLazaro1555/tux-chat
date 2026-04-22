# bot/handlers/commands.py - Telegram command handlers.

"""Telegram command handlers."""

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import DEFAULT_MODEL
from bot.memory.session import SessionManager

# Lista de modelos conocidos (puedes obtenerla dinámicamente desde Ollama después)
KNOWN_MODELS = [
    "deepseek-r1:14b",
    "deepseek-r1:8b",
    "qwen3:14b",
    "qwen3:8b",
    "llama3.2:3b",
    "mannix/qwen2.5-coder:32b-iq3_xxs",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message."""
    if update.effective_message is None:
        return
    current_model = context.bot_data.get("current_model", DEFAULT_MODEL)
    await update.effective_message.reply_text(
        "🐧 *Bienvenido a Tux Chat!*\n\n"
        "Soy un bot conectado a una IA local (Ollama).\n"
        "Puedes enviarme mensajes de texto y te responderé.\n\n"
        "*Comandos disponibles:*\n"
        "/start - Mostrar este mensaje\n"
        "/reset - Reiniciar la conversación (borrar historial)\n"
        "/model <nombre> - Cambiar el modelo de IA\n"
        "/models - Listar modelos disponibles\n"
        "/help - Ayuda adicional\n\n"
        "*Modelo actual:* `{}`".format(current_model),
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset conversation history for the user."""
    if update.effective_message is None or update.effective_user is None:
        return
    user_id = update.effective_user.id
    session_manager: SessionManager = context.bot_data["session_manager"]
    session_manager.reset_context(user_id)
    await update.effective_message.reply_text(
        "🧹 *Historial de conversación reiniciado.*", parse_mode="Markdown"
    )


async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available models."""
    if update.effective_message is None:
        return
    models_list = "\n".join([f"- `{m}`" for m in KNOWN_MODELS])
    current = context.bot_data.get("current_model", DEFAULT_MODEL)
    await update.effective_message.reply_text(
        f"🧠 *Modelos disponibles:*\n{models_list}\n\n"
        f"*Modelo actual:* `{current}`\n"
        f"Para cambiar: `/model nombre_del_modelo`",
        parse_mode="Markdown",
    )


async def change_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change the AI model for the current user."""
    if update.effective_message is None or update.effective_user is None:
        return
    args = context.args
    if not args:
        await update.effective_message.reply_text(
            "❌ *Uso correcto:* `/model nombre_del_modelo`\n"
            "Ejemplo: `/model deepseek-r1:8b`",
            parse_mode="Markdown",
        )
        return

    requested_model = args[0]
    if requested_model not in KNOWN_MODELS:
        await update.effective_message.reply_text(
            f"❌ Modelo `{requested_model}` no reconocido.\n"
            f"Usa `/models` para ver los disponibles.",
            parse_mode="Markdown",
        )
        return

    # Aseguramos que user_data existe (si es None, lo creamos)
    if context.user_data is None:
        context.user_data = {}
    context.user_data["model"] = requested_model
    await update.effective_message.reply_text(
        f"✅ *Modelo cambiado a:* `{requested_model}`", parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "🤖 *Ayuda de Tux Chat*\n\n"
        "Envía cualquier mensaje de texto y la IA local responderá.\n"
        "Mantiene contexto de conversación (recuerda lo que dijiste antes).\n\n"
        "*Comandos:*\n"
        "/start - Inicio\n"
        "/reset - Borrar historial\n"
        "/model <nombre> - Cambiar modelo\n"
        "/models - Listar modelos\n"
        "/help - Este mensaje\n\n"
        "*Nota:* La IA corre en mi máquina local, puede tener latencia.",
        parse_mode="Markdown",
    )
