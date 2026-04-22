# bot/handlers/text.py - Handler for plain text messages.

import re

from telegram import Update
from telegram.ext import ContextTypes

from bot.ai.ollama_text import OllamaTextClient
from bot.database import save_message  # <-- NUEVO: guardar en BD
from bot.memory.session import SessionManager
from bot.prompts.loader import load_prompt
from bot.utils.text import split_long_message


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user text message and reply with AI response."""
    if update.effective_message is None or update.effective_user is None:
        return

    user_id = update.effective_user.id
    user_message = update.effective_message.text
    if not user_message:
        return

    # --- Guardar mensaje del usuario en la base de datos ---
    save_message(user_id, "user", user_message)

    # ========== INYECCIÓN DE DOCUMENTO CON PLANTILLAS EXTERNAS ==========
    doc_text = None
    doc_name = None
    if context.user_data:
        doc_text = context.user_data.get("document_text")
        doc_name = context.user_data.get("document_name")

    if doc_text:
        lower_q = user_message.lower()
        es_pregunta_resumen = any(
            phrase in lower_q
            for phrase in [
                "contexto",
                "resume",
                "de qué trata",
                "qué contiene",
                "dame un contexto",
                "háblame del",
                "explica de que",
                "resumen",
                "síntesis",
                "qué hay en",
                "qué dice",
            ]
        )

        template_name = "document/summary" if es_pregunta_resumen else "document/query"
        user_message = load_prompt(
            template_name,
            variables={
                "doc_name": doc_name or "documento",
                "doc_content": doc_text,
                "user_question": user_message,
            },
        )
    # ====================================================================

    # Indicador de escritura
    await update.effective_message.chat.send_action(action="typing")

    # Obtener cliente de IA y session manager
    ai_client: OllamaTextClient = context.bot_data["ai_client"]
    session_manager: SessionManager = context.bot_data["session_manager"]

    # Obtener modelo para este usuario o el global
    model = None
    if context.user_data:
        model = context.user_data.get("model")
    if not model:
        model = context.bot_data.get("current_model")

    # Obtener contexto previo (tokens de Ollama)
    prev_context = session_manager.get_context(user_id)

    try:
        # Generar respuesta
        response, new_context = await ai_client.generate(
            prompt=user_message, model=model, context=prev_context
        )

        # Guardar nuevo contexto de Ollama (memoria de conversación)
        if new_context:
            session_manager.set_context(user_id, new_context)

        # Guardar histórico opcional en memoria (por si acaso)
        session_manager.add_exchange(user_id, user_message, response)

        # --- Guardar respuesta del bot en la base de datos ---
        save_message(user_id, "assistant", response)

        # --- Conversión de Markdown a HTML ---
        response = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response)
        response = re.sub(r"\*(.*?)\*", r"<i>\1</i>", response)

        # Partir respuesta larga y enviar
        chunks = split_long_message(response)
        for chunk in chunks:
            await update.effective_message.reply_text(chunk, parse_mode="HTML")

    except TimeoutError:
        await update.effective_message.reply_text(
            "⏰ *La IA local está tardando demasiado.*\n"
            "Intenta con un modelo más pequeño (ej. `llama3.2:3b`) o revisa que Ollama esté funcionando.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.effective_message.reply_text(
            f"❌ *Error al consultar la IA:*\n```\n{str(e)}\n```\n"
            "Verifica que Ollama esté corriendo (`ollama serve`) y que el modelo esté disponible.",
            parse_mode="Markdown",
        )
