"""
CONTEXTO: Generador de HTML para el sitio Buena Muerte. Lee y escribe
          los archivos HTML/JS del sitio para mantenerlos sincronizados.
ÍNDICE DE NAVEGACIÓN
[001] CONFIG / RUTAS        - línea 12
[002] TOUR — FECHAS[]       - línea 20
[003] NEWS — news.html      - línea 55
[004] BAND — band.html      - línea 110
"""
import os
import re
from datetime import datetime

# [001] CONFIG / RUTAS
SITE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _read(rel_path):
    path = os.path.join(SITE_ROOT, rel_path)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write(rel_path, content):
    path = os.path.join(SITE_ROOT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# [002] TOUR — FECHAS[]
def get_fechas():
    js = _read("assets/js.js")
    match = re.search(r"var FECHAS\s*=\s*\[(.*?)\];", js, re.DOTALL)
    if not match:
        return []
    block = match.group(1).strip()
    if not block:
        return []
    fechas = []
    for obj_match in re.finditer(r"\{(.*?)\}", block, re.DOTALL):
        obj_str = obj_match.group(1)
        fecha = {}
        for kv in re.finditer(r"(\w+)\s*:\s*['\"]([^'\"]*)['\"]", obj_str):
            fecha[kv.group(1)] = kv.group(2)
        arr_match = re.search(r"fotos\s*:\s*\[(.*?)\]", obj_str, re.DOTALL)
        if arr_match:
            urls = re.findall(r"['\"]([^'\"]+)['\"]", arr_match.group(1))
            fecha["fotos"] = urls
        if fecha:
            fechas.append(fecha)
    return fechas


def save_fechas(fechas):
    js = _read("assets/js.js")
    lines = []
    for i, f in enumerate(fechas):
        parts = []
        for k in ["dia", "mes", "anio", "lugar", "ciudad", "link", "mapa", "transporte", "descripcion"]:
            if k in f and f[k]:
                parts.append(f"    {k}: '{f[k]}'")
        if f.get("fotos"):
            fotos_str = ", ".join(f"'{url}'" for url in f["fotos"])
            parts.append(f"    fotos: [{fotos_str}]")
        lines.append("  {\n" + ",\n".join(parts) + "\n  }" + ("," if i < len(fechas) - 1 else ""))
    block = "\n".join(lines)
    new_js = re.sub(
        r"var FECHAS\s*=\s*\[.*?\];",
        f"var FECHAS = [\n{block}\n];",
        js,
        flags=re.DOTALL,
    )
    _write("assets/js.js", new_js)


# [003] NEWS — news.html
def get_news():
    html = _read("news.html")
    articles = []
    for m in re.finditer(
        r'<article class="news-item">(.*?)</article>', html, re.DOTALL
    ):
        block = m.group(1)
        title_m = re.search(r"<h3>(.*?)</h3>", block)
        date_m = re.search(r'<div class="news-item__date"><b>(.*?)</b>(.*?)</div>', block)
        thumb_m = re.search(r'<img class="news-item__thumb" src="(.*?)"', block)
        body_m = re.search(r'<div class="news-item__body">.*?<p>(.*?)</p>', block, re.DOTALL)
        articles.append({
            "title": title_m.group(1) if title_m else "",
            "date_day": date_m.group(1) if date_m else "",
            "date_text": date_m.group(2) if date_m else "",
            "thumb": thumb_m.group(1) if thumb_m else "",
            "body": body_m.group(1) if body_m else "",
        })
    return articles


def save_news(articles):
    html = _read("news.html")
    items = []
    for a in articles:
        items.append(
            f'        <article class="news-item">\n'
            f'          <img class="news-item__thumb" src="{a["thumb"]}" alt="{a["title"]}" loading="lazy">\n'
            f'          <div class="news-item__body">\n'
            f'            <div class="news-item__date"><b>{a["date_day"]}</b>{a["date_text"]}</div>\n'
            f'            <h3>{a["title"]}</h3>\n'
            f'            <p>{a["body"]}</p>\n'
            f'          </div>\n'
            f'          <a href="video.html" class="news-item__more">Videos ›</a>\n'
            f'        </article>'
        )
    new_block = "\n\n".join(items)
    new_html = re.sub(
        r'(<div class="news-list">).*?(</div>\s*</div>\s*</div>\s*<!-- \[004\])',
        f"\\1\n{new_block}\n      \\2",
        html,
        flags=re.DOTALL,
    )
    _write("news.html", new_html)


# [004] BAND — band.html
def get_members():
    html = _read("band.html")
    members = []
    for m in re.finditer(r'<article class="member">(.*?)</article>', html, re.DOTALL):
        block = m.group(1)
        name_m = re.search(r"<h3>(.*?)</h3>", block)
        role_m = re.search(r'<span class="member__role">(.*?)</span>', block)
        img_m = re.search(r'<img[^>]*src="(.*?)"', block)
        members.append({
            "name": name_m.group(1) if name_m else "",
            "role": role_m.group(1) if role_m else "",
            "photo": img_m.group(1) if img_m else "",
        })
    return members


def get_bio():
    html = _read("band.html")
    m = re.search(r'<div class="bio">(.*?)</div>', html, re.DOTALL)
    if not m:
        return ""
    bio_html = m.group(1)
    text = re.sub(r"<[^>]+>", "", bio_html).strip()
    return text


# [005] VIDEOS — video.html
def get_videos():
    html = _read("video.html")
    videos = []
    for m in re.finditer(r'data-video="([^"]+)"', html):
        vid_id = m.group(1)
        cat_m = re.search(r'data-category="([^"]*)"', html[max(0, m.start() - 200):m.start() + 200])
        title_m = re.search(r'class="video-slide__cat">(.*?)</p>', html[m.start():m.start() + 500])
        videos.append({
            "id": vid_id,
            "title": title_m.group(1) if title_m else vid_id,
            "category": cat_m.group(1) if cat_m else "",
        })
    return videos


def save_videos(videos):
    html = _read("video.html")
    slides = []
    for v in videos:
        vid = v["id"]
        title = v.get("title", vid)
        cat = v.get("category", "")
        wa_text = (title + " https://www.youtube.com/watch?v=" + vid).replace(" ", "%20")
        fb_url = "https://www.youtube.com/watch?v=" + vid
        slides.append(
            f'      <div class="video-slide" data-category="{cat}">\n'
            f'        <div class="video-thumb" data-video="{vid}" tabindex="0" role="button" aria-label="Reproducir">\n'
            f'          <img src="https://img.youtube.com/vi/{vid}/hqdefault.jpg" alt="{title}" loading="lazy">\n'
            f'          <span class="video-thumb__play">&#9654;</span>\n'
            f'        </div>\n'
            f'        <p class="video-slide__cat">{title}</p>\n'
            f'        <div class="video-share-row">\n'
            f'          <a class="video-share-btn video-share-btn--wa" href="https://api.whatsapp.com/send?text={wa_text}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24" width="14" height="14"><path d="M17.47 14.38c-.29-.14-1.7-.84-1.96-.93-.27-.1-.46-.15-.65.14-.2.29-.74.93-.9 1.12-.17.2-.33.22-.62.07-.29-.14-1.22-.45-2.33-1.43-.86-.77-1.44-1.71-1.61-2-.17-.29-.02-.44.13-.58.13-.13.29-.33.43-.5.14-.17.19-.29.29-.48.1-.2.05-.36-.02-.5-.08-.15-.65-1.56-.89-2.14-.24-.56-.48-.48-.65-.49h-.56c-.2 0-.5.07-.76.36-.26.29-1 1-1 2.42s1.02 2.79 1.17 2.98c.14.2 2.01 3.07 4.88 4.31.68.3 1.21.47 1.63.61.68.22 1.3.19 1.79.12.55-.08 1.7-.7 1.94-1.37.24-.67.24-1.25.17-1.37-.08-.12-.27-.2-.56-.34z"/><path d="M12 2C6.48 2 2 6.48 2 12c0 1.77.46 3.43 1.27 4.88L2 22l5.23-1.23A9.94 9.94 0 0 0 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18a8 8 0 0 1-4.28-1.24l-.31-.18-3.09.73.73-3.01-.2-.32A8 8 0 1 1 12 20z" fill="none"/></svg></a>\n'
            f'          <a class="video-share-btn video-share-btn--fb" href="https://www.facebook.com/sharer/sharer.php?u={fb_url}" target="_blank" rel="noopener" aria-label="Facebook"><svg viewBox="0 0 24 24" width="14" height="14"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.45 2.89h-2.33v6.99A10 10 0 0 0 22 12z"/></svg></a>\n'
            f'          </div>\n'
            f'      </div>'
        )
    new_grid = "\n\n".join(slides)
    new_html = re.sub(
        r'(<div class="video-grid"[^>]*>).*?(</div>\s*</div>\s*</div>\s*<!-- \[004\])',
        f"\\1\n{new_grid}\n    \\2",
        html,
        flags=re.DOTALL,
    )
    _write("video.html", new_html)
