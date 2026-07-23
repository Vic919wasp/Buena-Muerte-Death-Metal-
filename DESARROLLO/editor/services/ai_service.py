"""
CONTEXTO: Cliente del servicio Ollama para IA local. Provee funciones
          de chat, análisis de código y generación de texto mejorado.
          100% offline, sin dependencias externas.
ÍNDICE DE NAVEGACIÓN
[001] CONFIG / CONSTANTES    - línea 12
[002] CLIENTE OLLAMA         - línea 20
[003] CHAT / COMPLETION      - línea 35
[004] ANÁLISIS DE CÓDIGO     - línea 60
[005] GENERACIÓN DE TEXTO    - línea 85
[006] UTILIDADES             - línea 110
"""
import json
import requests
from typing import Optional, Generator

# [001] CONFIG / CONSTANTES
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
TIMEOUT_SECONDS = 90


# [002] CLIENTE OLLAMA
class OllamaClient:
    """Cliente ligero para la API de Ollama."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _endpoint(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def is_available(self) -> bool:
        """Verifica que Ollama esté corriendo y el modelo disponible."""
        try:
            r = requests.get(self._endpoint("/api/tags"), timeout=5)
            if r.status_code != 200:
                return False
            models = [m["name"] for m in r.json().get("models", [])]
            return self.model in models or f"{self.model}:latest" in models
        except (requests.ConnectionError, requests.Timeout):
            return False

    def list_models(self) -> list:
        """Lista modelos disponibles."""
        try:
            r = requests.get(self._endpoint("/api/tags"), timeout=5)
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
        except (requests.ConnectionError, requests.Timeout):
            pass
        return []


# [003] CHAT / COMPLETION
def chat(messages: list, model: str = OLLAMA_MODEL,
         temperature: float = 0.7, stream: bool = False) -> str:
    """
    Envía mensajes al modelo y retorna la respuesta completa.
    messages: [{"role": "user"/"assistant", "content": "..."}]
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": temperature, "num_predict": 300},
    }
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")
    except requests.ConnectionError:
        return "[Error: Ollama no está corriendo. Iniciá Ollama y reintentá.]"
    except requests.Timeout:
        return "[Error: La respuesta tardó demasiado. Intentá con un prompt más corto.]"
    except Exception as e:
        return f"[Error inesperado: {e}]"


def chat_stream(messages: list, model: str = OLLAMA_MODEL,
                temperature: float = 0.7) -> Generator[str, None, None]:
    """Versión streaming del chat — genera tokens uno a uno."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature, "num_predict": 300},
    }
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=TIMEOUT_SECONDS,
            stream=True,
        )
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                if token:
                    yield token
    except (requests.ConnectionError, requests.Timeout):
        yield "[Error: Ollama no disponible]"


# [004] ANÁLISIS DE CÓDIGO
def analyze_code(code: str, filename: str = "") -> str:
    """Analiza código y sugiere mejoras."""
    system = (
        "Sos un asistente técnico especializado en Python/PySide6/Qt. "
        "Analizá el código dado y sugerí mejoras concretas: bugs potenciales, "
        "optimizaciones, mejores prácticas. Respondé en español, sé conciso."
    )
    user_msg = f"Analizá este código{' de ' + filename if filename else ''}:\n\n```\n{code}\n```"
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ])


def improve_text(text: str, context: str = "", style: str = "metal") -> str:
    """Mejora un texto dado manteniendo el tono."""
    styles = {
        "metal": (
            "Sos un redactor de contenido metal/underground argentino. "
            "Mejorá el texto para que sea más impactante, use lenguaje de la "
            "escena metal (grosero, directo, pasional), manteniendo la info. "
            "Usá mayúsculas para énfasis, emojis de metal (🤘🔥💀), "
            "y un tono que conecte con la banda de metal."
        ),
        "news": (
            "Sos un periodista de música extrema. Redactá una noticia "
            "profesional pero con onda underground. Incluí datos concretos."
        ),
        "formal": (
            "Sos un editor profesional. Mejorá la gramática y claridad "
            "del texto sin cambiar el tono."
        ),
    }
    system = styles.get(style, styles["metal"])
    ctx = f"\nContexto adicional: {context}" if context else ""
    user_msg = f"Mejorá este texto:{ctx}\n\n---\n{text}\n---\n\nVersión mejorada:"
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ])


# [005] GENERACIÓN DE TEXTO
def generate_post(event_info: dict, scene_context: str = "") -> str:
    """Genera un post/redes para un evento de la banda."""
    system = (
        "Sos el community manager de Buena Muerte, banda de death metal de "
        "Zona Sur, AMBA, Argentina. Generá un post para redes sociales "
        "(Instagram/Facebook) para un show. Sé creativo, usá hashtags "
        "relevantes, emojis de metal, y un tono que genere expectativa. "
        "Incluí fecha, lugar y cómo conseguir entradas."
    )
    info_str = json.dumps(event_info, ensure_ascii=False, indent=2)
    ctx = f"\nContexto de la escena ARG:\n{scene_context}" if scene_context else ""
    user_msg = f"Generá un post para este show:\n\n{info_str}{ctx}"
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ])


def generate_description(event_info: dict) -> str:
    """Genera la descripción mejorada de una fecha de tour."""
    system = (
        "Sos el redactor de Buena Muerte. Generá una descripción atractiva "
        "para una fecha de tour. El tono es death metal argentino: directo, "
        "crudo, apasionado. Incluí: hora, precio si hay, bandas invitadas, "
        "cómo llegar, y por qué no perderse el show."
    )
    info_str = json.dumps(event_info, ensure_ascii=False, indent=2)
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": f"Describí esta fecha:\n\n{info_str}"},
    ])


# [006] WEB SCRAPING PARA AI
def scrape_url(url: str) -> str:
    """Scrapea una URL y retorna el texto extraído."""
    try:
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return text[:4000]
    except Exception as e:
        return f"[Error al scrapear {url}: {e}]"


# [006] UTILIDADES
def quick_prompt(prompt: str, system: str = "") -> str:
    """Función rápida para un prompt simple."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(messages)
