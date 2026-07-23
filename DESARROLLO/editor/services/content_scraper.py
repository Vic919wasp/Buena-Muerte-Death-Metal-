"""
CONTEXTO: Scraper de contenido para pipeline de publicación.
          Busca noticias, bios, imágenes de fuentes ARG y retorna
          contenido estructurado para que la AI genere notas.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONFIG        - línea 12
[002] FUENTES                 - línea 20
[003] SCRAPERS                - línea 40
[004] PIPELINE                - línea 100
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# [001] FUENTES
SOURCES = {
    "metaleyewitness": {
        "name": "Metal Eye Witness",
        "url": "https://metaleyewitness.com",
        "type": "news",
    },
    "icarusmusic": {
        "name": "Icarus Music",
        "url": "https://www.icarusmusic.com",
        "type": "news",
    },
    "madhouse": {
        "name": "Madhouse Magazine",
        "url": "https://www.madhousemagazine.com",
        "type": "news",
    },
    "delotrolado": {
        "name": "Del Otro Lado",
        "url": "https://www.delotrolado.com.ar",
        "type": "news",
    },
    "bsasmetalshows": {
        "name": "BsAs Metal Shows",
        "url": "https://www.buenosairesmetal.com",
        "type": "shows",
    },
    "metaldaze": {
        "name": "Metal Daze",
        "url": "https://www.metaldaze.com.ar",
        "type": "news",
    },
    "revistaimpuridad": {
        "name": "Revista Impuridad",
        "url": "https://www.revistaimpuridad.com",
        "type": "news",
    },
    "elgigantedelaplata": {
        "name": "El Gigante de la Plata",
        "url": "https://elgigantedelaplata.com",
        "type": "news",
    },
    "claseb": {
        "name": "Clase B Rock y Metal",
        "url": "https://claseb.net",
        "type": "news",
    },
    "rockaxes": {
        "name": "Rockaxes",
        "url": "https://www.rockaxes.com",
        "type": "news",
    },
    "bravewords": {
        "name": "Brave Words",
        "url": "https://bravewords.com",
        "type": "international",
    },
    "metalinjection": {
        "name": "Metal Injection",
        "url": "https://www.metalinjection.net",
        "type": "international",
    },
    "metalsucks": {
        "name": "MetalSucks",
        "url": "https://metalsucks.net",
        "type": "international",
    },
    "decibelmagazine": {
        "name": "Decibel Magazine",
        "url": "https://www.decibelmagazine.com",
        "type": "international",
    },
    "blabbermouth": {
        "name": "Blabbermouth",
        "url": "https://www.blabbermouth.net",
        "type": "international",
    },
    "loudwire": {
        "name": "Loudwire",
        "url": "https://loudwire.com",
        "type": "international",
    },
    "metalkaoz": {
        "name": "Metal Kaoz",
        "url": "https://www.metalkaoz.com",
        "type": "international",
    },
    "spiritofmetal": {
        "name": "Spirit of Metal",
        "url": "https://www.spirit-of-metal.com",
        "type": "international",
    },
    "metalarch": {
        "name": "Metal Archives",
        "url": "https://www.metal-archives.com",
        "type": "database",
    },
    "setlistfm": {
        "name": "Setlist.fm",
        "url": "https://www.setlist.fm",
        "type": "database",
    },
    "spotify": {
        "name": "Spotify",
        "url": "https://open.spotify.com",
        "type": "streaming",
    },
}


# [002] SCRAPERS
def scrape_url(url: str, max_chars: int = 4000) -> dict:
    """Scrapea una URL y retorna contenido estructurado."""
    try:
        r = requests.get(url, timeout=15, headers=HEADERS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        text = re.sub(r'\n{3,}', '\n\n', text)

        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if not src.startswith("http"):
                from urllib.parse import urljoin
                src = urljoin(url, src)
            if any(ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                images.append(src)

        return {
            "url": url,
            "title": title,
            "text": text[:max_chars],
            "images": images[:5],
            "ok": True,
        }
    except Exception as e:
        return {"url": url, "error": str(e), "ok": False}


def scrape_source(source_key: str) -> dict:
    """Scrapea una fuente configurada."""
    src = SOURCES.get(source_key)
    if not src:
        return {"error": f"Fuente '{source_key}' no encontrada"}
    return scrape_url(src["url"])


def search_web(query: str, num_results: int = 5) -> list:
    """Busca en la web usando DuckDuckGo HTML (sin API key)."""
    try:
        url = "https://html.duckduckgo.com/html/"
        r = requests.post(url, data={"q": query}, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for a in soup.select("a.result__a")[:num_results]:
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if href and title:
                results.append({"title": title, "url": href})
        return results
    except Exception:
        return []


# [003] PIPELINE
def fetch_article(url: str) -> dict:
    """Trae un artículo completo de una URL, extrae texto, imagen y título."""
    data = scrape_url(url, max_chars=6000)
    if not data.get("ok"):
        return data

    text = data["text"]
    sentences = text.split(".")
    intro = ". ".join(sentences[:10]).strip() + "."
    body = "\n\n".join(sentences[i:i+5] for i in range(0, len(sentences), 5)[:6])
    body = ". ".join(body.split(". ")[0:30]) + "."

    return {
        "url": url,
        "title": data["title"],
        "intro": intro[:500],
        "body": body[:2000],
        "images": data["images"],
        "ok": True,
    }


def scrape_social_media(band_name: str = "Buena Muerte") -> dict:
    """Busca y scrapea redes sociales de la banda."""
    results = {"texts": [], "images": [], "sources": []}

    queries_social = [
        f"{band_name} instagram.com",
        f"{band_name} facebook.com",
        f"{band_name} youtube.com canal",
        f"{band_name} spotify artista",
        f"{band_name} tiktok",
        f"{band_name} twitter OR x.com",
    ]
    for q in queries_social:
        search_results = search_web(q, num_results=3)
        for r in search_results[:2]:
            url = r["url"]
            if url in results["sources"]:
                continue
            is_social = any(s in url for s in [
                "instagram.com", "facebook.com", "youtube.com",
                "spotify.com", "open.spotify.com", "tiktok.com",
                "twitter.com", "x.com"
            ])
            if is_social:
                data = scrape_url(url, max_chars=2000)
                if data.get("ok") and data.get("text"):
                    txt = data["text"]
                    if len(txt) > 50:
                        results["texts"].append(f"[{r['title']}]({url})\n{txt[:1500]}")
                        results["images"].extend(data.get("images", [])[:3])
                        results["sources"].append(url)

    consolidated = "\n\n---\n\n".join(results["texts"])
    return {
        "text": consolidated[:6000],
        "images": results["images"][:8],
        "sources": results["sources"],
        "ok": bool(results["texts"]),
    }


def fetch_band_info(band_name: str = "Buena Muerte") -> dict:
    """Busca info de la banda en múltiples fuentes y consolida."""
    results = {"texts": [], "images": [], "sources": []}

    site_url = "https://buena-muerte-death-metal.onrender.com"
    site = scrape_url(site_url, max_chars=3000)
    if site.get("ok"):
        results["texts"].append(f"[Sitio oficial]\n{site['text']}")
        results["images"].extend(site.get("images", []))
        results["sources"].append(site_url)

    queries = [
        f'"{band_name}" integrantes miembros banda',
        f'"{band_name}" baterista guitarrista bajista',
        f'"{band_name}" "Favio Leguizamón" bio',
        f'"{band_name}" death metal Argentina Zona Sur',
        f'"{band_name}" Catalepsia 2024 review',
        f'"{band_name}" shows conciertos Argentina 2024 2025',
        f'"{band_name}" Instagram Facebook',
        f'"{band_name}" youtube canal',
        f'"{band_name}" Spotify Apple Music',
    ]
    for q in queries:
        search_results = search_web(q, num_results=5)
        for r in search_results[:3]:
            url = r["url"]
            if any(skip in url for skip in ["twitter.com", "x.com", "tiktok.com"]):
                continue
            if url in results["sources"]:
                continue
            article = scrape_url(url, max_chars=2500)
            if article.get("ok") and article.get("text"):
                txt = article["text"]
                if len(txt) > 100:
                    results["texts"].append(f"[{r['title']}]({url})\n{txt[:2000]}")
                    results["images"].extend(article.get("images", [])[:2])
                    results["sources"].append(url)

    consolidated = "\n\n---\n\n".join(results["texts"])

    social = scrape_social_media(band_name)
    if social.get("ok"):
        consolidated += "\n\n--- REDES SOCIALES ---\n\n" + social["text"]
        results["images"].extend(social.get("images", []))
        results["sources"].extend(social.get("sources", []))

    return {
        "text": consolidated[:12000],
        "images": results["images"][:10],
        "sources": results["sources"],
        "ok": bool(results["texts"]),
    }


def batch_scrape(urls: list) -> list:
    """Scrapea múltiples URLs en lote."""
    results = []
    for url in urls:
        results.append(fetch_article(url))
    return results


def fetch_member_info(band_name: str, role: str) -> dict:
    """Busca info específica de un integrante por rol."""
    results = {"texts": [], "images": [], "sources": []}
    blocked = ["metal-archives.com", "twitter.com", "x.com"]

    site_url = "https://buena-muerte-death-metal.onrender.com"
    site = scrape_url(site_url, max_chars=3000)
    if site.get("ok"):
        results["texts"].append(f"[Sitio oficial]\n{site['text']}")
        results["sources"].append(site_url)

    queries = [
        f'"{band_name}" {role}',
        f'{band_name} {role} nombre',
        f'"{band_name}" {role} biografia',
        f'"{band_name}" {role} Argentina metal',
        f'{band_name} banda {role} who is',
        f'"{band_name}" {role} instagram',
        f'"{band_name}" {role} entrevista interview',
        f'"{band_name}" members lineup',
    ]
    for q in queries:
        search_results = search_web(q, num_results=5)
        for r in search_results[:3]:
            url = r["url"]
            if any(skip in url for skip in blocked):
                continue
            if url in results["sources"]:
                continue
            article = scrape_url(url, max_chars=2500)
            if article.get("ok") and article.get("text") and len(article["text"]) > 50:
                txt = article["text"]
                results["texts"].append(f"[{r['title']}]({url})\n{txt[:2000]}")
                results["images"].extend(article.get("images", [])[:2])
                results["sources"].append(url)

    consolidated = "\n\n---\n\n".join(results["texts"])
    if not consolidated.strip() or len(consolidated) < 200:
        consolidated = (
            f"La búsqueda web sobre el {role} de {band_name} no arrojó resultados "
            f"suficientes. Esto puede deberse a que la banda es underground y no "
            f"tiene presencia pública documentada de sus integrantes. "
            f"Se encontró info del sitio oficial pero sin datos específicos del {role}."
        )
    return {
        "text": consolidated[:10000],
        "images": results["images"][:10],
        "sources": results["sources"],
        "ok": bool(results["texts"]),
    }
