from pathlib import Path

PROMPTS_DIR = Path(__file__).parent

def load_prompt(name: str = "default") -> str:
    prompt_file = PROMPTS_DIR / f"{name}.txt"
    if not prompt_file.exists():
        return "Eres un asistente útil. Responde de forma concisa (menos de 4000 caracteres)."
    return prompt_file.read_text(encoding="utf-8").strip()
