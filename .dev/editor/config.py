"""
CONTEXTO: Configuración del editor — API keys, rutas, settings.
ÍNDICE DE NAVEGACIÓN
[001] CONFIG PATHS             - línea 12
[002] API KEYS                 - línea 18
[003] HELPERS                  - línea 30
"""
import json
import os

# [001] CONFIG PATHS
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..")
CONFIG_FILE = os.path.join(CONFIG_DIR, "editor_config.json")

# [002] API KEYS — defaults
DEFAULTS = {
    "gemini_api_key": "",
    "ai_backend": "gemini",  # "ollama" | "gemini"
    "gemini_model": "gemini-2.0-flash",
}

# [003] HELPERS
def load_config() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg

def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def get(key: str):
    return load_config().get(key, DEFAULTS.get(key))

def set(key: str, value):
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
