# bot/handlers/document.py - Handler for document uploads (PDF, DOCX, TXT)

import io

import docx
import PyPDF2
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import save_message  # <-- NUEVO: guardar en BD


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process uploaded document, extract text, store in DB and session."""
    if update.effective_message is None or update.effective_user is None:
        return

    user_id = update.effective_user.id
    document = update.effective_message.document
    if not document:
        return

    # Notificar que se está procesando
    await update.effective_message.chat.send_action(action="typing")

    # Obtener nombre y extensión
    file_name = document.file_name or "documento"
    ext = file_name.split(".")[-1].lower()

    # Descargar archivo
    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()

    text = ""
    try:
        if ext == "pdf":
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == "txt":
            text = file_bytes.decode("utf-8")
        else:
            await update.effective_message.reply_text(
                f"Formato `.{ext}` no soportado. Usa PDF, DOCX o TXT.",
                parse_mode="Markdown",
            )
            return
    except Exception as e:
        await update.effective_message.reply_text(f"Error al leer el archivo: {e}")
        return

    if not text.strip():
        await update.effective_message.reply_text(
            "No se pudo extraer texto del documento."
        )
        return

    # Limitar tamaño para no saturar el contexto
    MAX_CHARS = 8000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "\n\n[Documento truncado por ser muy largo]"

    # --- Guardar en base de datos como mensaje del usuario ---
    contenido_bd = f"[Documento: {file_name}]\n\n{text}"
    save_message(user_id, "user", contenido_bd)

    # --- Guardar en user_data para la sesión actual (opcional) ---
    if context.user_data is None:
        context.user_data = {}
    context.user_data["document_text"] = text
    context.user_data["document_name"] = file_name

    await update.effective_message.reply_text(
        f"✅ Documento `{file_name}` procesado.\n"
        f"Caracteres extraídos: {len(text)}\n"
        "El contenido se ha guardado en el historial. Ahora puedes preguntarme sobre él.",
        parse_mode="Markdown",
    )
