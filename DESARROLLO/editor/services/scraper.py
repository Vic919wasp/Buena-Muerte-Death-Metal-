"""
CONTEXTO: Scraper de la escena metal argentina. Recopila shows próximos,
          noticias y contexto de las principales fuentes del underground.
          Usa requests + BeautifulSoup para scraping ligero.
ÍNDICE DE NAVEGACIÓN
[001] CONFIG / CONSTANTES    - línea 13
[002] FUENTES                - línea 22
[003] SCRAPERS POR FUENTE    - línea 45
[004] ORQUESTADOR            - línea 120
[005] CACHE                  - línea 145
"""
import os
import json
import time
import re
from datetime import datetime
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# [001] CONFIG / CONSTANTES
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, "metal_scene.json")
CACHE_TTL_HOURS = 6
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}


# [002] FUENTES
FUENTES = {
    "metaleyewitness": {
        "name": "Metal Eye Witness",
        "url": "https://metaleyewitness.com/newsite/content/",
        "type": "agenda",
    },
    "icarusmusic": {
        "name": "Icarus Music",
        "url": "https://icarusmusicstore.com/29-recitales",
        "type": "recitales",
    },
    "madhouse": {
        "name": "Madhouse",
        "url": "https://madhouse.com.ar/category/visitas-pesadas/",
        "type": "noticias",
    },
    "delotrolado": {
        "name": "Del Otro Lado Metal",
        "url": "https://www.delotroladometal.com.ar/",
        "type": "noticias",
    },
    "bsasmetalshows": {
        "name": "Buenos Aires Metal Shows",
        "url": "https://bsasmetalshows.com.ar/",
        "type": "shows",
    },
    "metaldaze": {
        "name": "Metal-Daze",
        "url": "https://metaldazeweb.com/",
        "type": "noticias",
    },
}


# [003] SCRAPERS POR FUENTE
def _get_soup(url: str) -> Optional["BeautifulSoup"]:
    """Request genérico con manejo de errores."""
    if not HAS_BS4:
        return None
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception:
        return None


def scrape_metaleyewitness() -> list:
    """Scrapea la agenda de shows de Metal Eye Witness."""
    soup = _get_soup(FUENTES["metaleyewitness"]["url"])
    if not soup:
        return []
    shows = []
    for text in soup.stripped_strings:
        text = text.strip()
        if not text or len(text) < 10:
            continue
        match = re.search(
            r"(\d{1,2})/(\d{1,2})\s+(.+?)(?:,\s*(.+?))?$", text
        )
        if match:
            dia, mes, lugar = match.group(1), match.group(2), match.group(3)
            ciudad = match.group(4) or "Buenos Aires"
            shows.append({
                "fuente": "metaleyewitness",
                "fecha": f"{dia}/{mes}/2026",
                "lugar": lugar.strip(),
                "ciudad": ciudad.strip(),
                "raw": text,
            })
    return shows[:30]


def scrape_icarusmusic() -> list:
    """Scrapea recitales de Icarus Music."""
    soup = _get_soup(FUENTES["icarusmusic"]["url"])
    if not soup:
        return []
    shows = []
    for article in soup.find_all("article"):
        title_el = article.find(["h2", "h3", "h4"])
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link_el = article.find("a", href=True)
        link = link_el["href"] if link_el else ""
        shows.append({
            "fuente": "icarusmusic",
            "titulo": title,
            "link": link,
            "raw": title,
        })
    return shows[:20]


def scrape_madhouse() -> list:
    """Scrapea noticias de Madhouse."""
    soup = _get_soup(FUENTES["madhouse"]["url"])
    if not soup:
        return []
    articles = []
    for article in soup.find_all("article"):
        title_el = article.find(["h2", "h3"])
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link_el = article.find("a", href=True)
        link = link_el["href"] if link_el else ""
        excerpt_el = article.find("p")
        excerpt = excerpt_el.get_text(strip=True)[:200] if excerpt_el else ""
        articles.append({
            "fuente": "madhouse",
            "titulo": title,
            "link": link,
            "excerpto": excerpt,
        })
    return articles[:15]


def scrape_delotrolado() -> list:
    """Scrapea artículos de Del Otro Lado Metal."""
    soup = _get_soup(FUENTES["delotrolado"]["url"])
    if not soup:
        return []
    articles = []
    for article in soup.find_all("article"):
        title_el = article.find(["h2", "h3"])
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link_el = article.find("a", href=True)
        link = link_el["href"] if link_el else ""
        articles.append({
            "fuente": "delotrolado",
            "titulo": title,
            "link": link,
        })
    return articles[:15]


def scrape_bsasmetalshows() -> list:
    """Scrapea shows de Buenos Aires Metal Shows."""
    soup = _get_soup(FUENTES["bsasmetalshows"]["url"])
    if not soup:
        return []
    shows = []
    for article in soup.find_all("article"):
        title_el = article.find(["h2", "h3"])
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link_el = article.find("a", href=True)
        link = link_el["href"] if link_el else ""
        shows.append({
            "fuente": "bsasmetalshows",
            "titulo": title,
            "link": link,
        })
    return shows[:15]


def scrape_metaldaze() -> list:
    """Scrapea noticias de Metal-Daze."""
    soup = _get_soup(FUENTES["metaldaze"]["url"])
    if not soup:
        return []
    articles = []
    for article in soup.find_all("article"):
        title_el = article.find(["h2", "h3"])
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link_el = article.find("a", href=True)
        link = link_el["href"] if link_el else ""
        articles.append({
            "fuente": "metaldaze",
            "titulo": title,
            "link": link,
        })
    return articles[:15]


SCRAPERS = {
    "metaleyewitness": scrape_metaleyewitness,
    "icarusmusic": scrape_icarusmusic,
    "madhouse": scrape_madhouse,
    "delotrolado": scrape_delotrolado,
    "bsasmetalshows": scrape_bsasmetalshows,
    "metaldaze": scrape_metaldaze,
}


# [004] ORQUESTADOR
def scrape_all() -> dict:
    """Ejecuta todos los scrapers y retorna el resultado combinado."""
    if not HAS_BS4:
        return {"error": "BeautifulSoup no instalado. Ejecutá: pip install beautifulsoup4 lxml"}
    result = {
        "timestamp": datetime.now().isoformat(),
        "shows": [],
        "noticias": [],
        "raw_count": 0,
    }
    for name, scraper_fn in SCRAPERS.items():
        try:
            data = scraper_fn()
            for item in data:
                item["fuente_name"] = FUENTES[name]["name"]
            if FUENTES[name]["type"] in ("agenda", "recitales", "shows"):
                result["shows"].extend(data)
            else:
                result["noticias"].extend(data)
            result["raw_count"] += len(data)
        except Exception as e:
            result.setdefault("errors", []).append(f"{name}: {e}")
    _save_cache(result)
    return result


def get_scene_summary() -> str:
    """Retorna un resumen formateado de la escena para usar en prompts."""
    data = load_cache()
    if not data:
        data = scrape_all()
    lines = ["=== ESCENA METAL ARGENTINA ===\n"]
    if data.get("shows"):
        lines.append("SHOWS PRÓXIMOS:")
        for s in data["shows"][:15]:
            fecha = s.get("fecha", "")
            lugar = s.get("lugar", s.get("titulo", ""))
            ciudad = s.get("ciudad", "")
            fuente = s.get("fuente_name", "")
            lines.append(f"  - {fecha} | {lugar} | {ciudad} [{fuente}]")
    if data.get("noticias"):
        lines.append("\nNOTICIAS RECIENTES:")
        for n in data["noticias"][:10]:
            titulo = n.get("titulo", "")
            fuente = n.get("fuente_name", "")
            lines.append(f"  - {titulo} [{fuente}]")
    lines.append(f"\nTotal: {data.get('raw_count', 0)} items de {len(FUENTES)} fuentes")
    return "\n".join(lines)


# [005] CACHE
def _save_cache(data: dict):
    """Guarda datos en caché local."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_cache() -> Optional[dict]:
    """Carga caché si existe y no expiró."""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        mtime = os.path.getmtime(CACHE_FILE)
        age_hours = (time.time() - mtime) / 3600
        if age_hours > CACHE_TTL_HOURS:
            return None
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def force_refresh() -> dict:
    """Fuerza recarga de datos desde las fuentes."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    return scrape_all()
