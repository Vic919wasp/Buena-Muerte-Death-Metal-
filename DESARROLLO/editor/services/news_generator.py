"""
CONTEXTO: Generador de notas/editorial con AI.
          Toma contenido scrapeado y genera notas periodísticas
          con título, bajada, cuerpo e imagen para publicar.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS                  - línea 12
[002] GENERADOR DE NOTAS       - línea 20
[003] PROCESAMIENTO            - línea 80
"""
import json
from services import ai_service


# [001] GENERADOR DE NOTAS
def generate_news_article(scraped_data: dict, topic: str = "") -> dict:
    """Genera una nota periodística a partir de contenido scrapeado."""
    title = scraped_data.get("title", "")
    text = scraped_data.get("text", scraped_data.get("body", ""))
    url = scraped_data.get("url", "")

    system = (
        "Sos el periodista de Buena Muerte, death metal de Zona Sur, AMBA. "
        "ESCRIBÍ como las revistas especializadas de metal: Brave Words, "
        "Metal Injection, Decibel Magazine, Revista Impuridad, El Gigante "
        "de la Plata. Tono: directo, crudo, apasionado, técnico. "
        "Usá datos concretos: fechas, lugares, nombres, discografía.\n\n"
        "ESTILO EDITORIAL:\n"
        "- Título: impactante, corto, con gancho (tipo headline de Brave Words)\n"
        "- Bajada: 1-2 oraciones que resuman la nota estilo lead periodístico\n"
        "- Cuerpo: 3-5 párrafos, estilo feature de revista metal\n"
        "- Cerrá con un CTA o expectativa\n"
        "- NO inventes datos que no estén en el contenido fuente\n"
        "- Si la info es limitada, decilo honestamente\n"
        "- Tags: #BuenaMuerte #DeathMetal #MetalArgentino + tags relevantes\n"
        "- Respondé SOLO con el JSON, sin texto adicional\n\n"
        "REGLA ABSOLUTA: Todo dato que menciones DEBE estar en el contenido "
        "scrapeado. Si no está, no lo inventes. Preguntá o aclará que falta info."
    )

    user_msg = (
        f"Generá una nota periodística estilo revista metal basada en esta información:\n\n"
        f"TÍTULO FUENTE: {title}\n"
        f"URL: {url}\n"
        f"CONTENIDO SCRAPEADO:\n{text[:3000]}\n\n"
    )
    if topic:
        user_msg += f"ENFOQUE: {topic}\n\n"

    user_msg += (
        "Respondé con este JSON exacto:\n"
        '{"titulo": "...", "bajada": "...", "cuerpo": "...", '
        '"tags": ["tag1", "tag2", "tag3"]}'
    )

    result = ai_service.chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ])

    try:
        json_str = result
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        article = json.loads(json_str.strip())
        article["fuente_url"] = url
        article["fuente_nombre"] = title
        article["imagen_url"] = (scraped_data.get("images", [""])[0]
                                  if scraped_data.get("images") else "")
        article["fecha"] = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        article["ok"] = True
        return article
    except (json.JSONDecodeError, IndexError):
        return {
            "titulo": title or topic or "Nueva nota",
            "bajada": result[:200],
            "cuerpo": result,
            "tags": ["Buena Muerte", "Death Metal"],
            "fuente_url": url,
            "fuente_nombre": title,
            "imagen_url": "",
            "fecha": __import__("datetime").datetime.now().strftime("%Y-%m-%d"),
            "ok": False,
            "raw": result,
        }


def improve_article(article: dict, instruction: str = "") -> dict:
    """Mejora una nota existente con un prompt adicional."""
    system = (
        "Sos un editor de música extrema. Mejorá la nota periodística "
        "dada manteniendo los hechos correctos. Respondé con el mismo "
        "formato JSON."
    )
    user_msg = f"Nota actual:\n\n{json.dumps(article, ensure_ascii=False, indent=2)}"
    if instruction:
        user_msg += f"\n\nInstrucción de mejora: {instruction}"

    result = ai_service.chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ])

    try:
        json_str = result
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        improved = json.loads(json_str.strip())
        improved["fuente_url"] = article.get("fuente_url", "")
        improved["imagen_url"] = article.get("imagen_url", "")
        improved["fecha"] = article.get("fecha", "")
        return improved
    except (json.JSONDecodeError, IndexError):
        article["cuerpo"] = result
        return article


# [002] PROCESAMIENTO
def generate_from_url(url: str, topic: str = "") -> dict:
    """Pipeline completo: scrapea URL → genera nota."""
    from services.content_scraper import fetch_article
    scraped = fetch_article(url)
    if not scraped.get("ok"):
        return {"error": scraped.get("error", "Error al scrapear"), "ok": False}
    return generate_news_article(scraped, topic)


def generate_from_topic(query: str) -> dict:
    """Busca en la web → scrapea primer resultado → genera nota."""
    from services.content_scraper import search_web
    results = search_web(query, num_results=3)
    if not results:
        return {"error": f"No se encontraron resultados para: {query}", "ok": False}
    return generate_from_url(results[0]["url"], topic=query)
