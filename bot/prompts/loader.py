# bot/prompts/loader.py - Loader for prompt templates.

from pathlib import Path
from typing import Any, Dict, Optional

PROMPTS_DIR = Path(__file__).parent


def load_prompt(
    name: str = "default", variables: Optional[Dict[str, Any]] = None
) -> str:
    """Load a prompt from a .txt file and replace {{var}} placeholders."""
    # Buscar primero en la raíz de prompts
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if not prompt_file.exists():
        # Buscar en subcarpeta document/
        prompt_file = PROMPTS_DIR / "document" / f"{name}.txt"
        if not prompt_file.exists():
            return "Eres un asistente útil. Responde en español."

    text = prompt_file.read_text(encoding="utf-8").strip()
    if variables:
        for key, value in variables.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
    return text


def list_prompts() -> list:
    """Return list of available prompt names."""
    prompts = [f.stem for f in PROMPTS_DIR.glob("*.txt")]
    doc_prompts = [f.stem for f in (PROMPTS_DIR / "document").glob("*.txt")]
    return prompts + [f"document/{p}" for p in doc_prompts]
