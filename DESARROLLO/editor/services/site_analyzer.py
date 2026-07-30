"""
CONTEXTO: Analizador de sitios web para generar site_config.json.
          Lee una URL o directorio de HTML, extrae la estructura
          de p�ginas, secciones y navegaci�n, y genera el
          archivo de configuraci�n para el editor configurado.
�NDICE DE NAVEGACI�N
[001] IMPORTS / CONFIG      - l�nea 14
[002] ANALIZADOR HTML       - l�nea 26
[003] EXTRACCI�N DE NAV    - l�nea 55
[004] DETECCI�N DE P�GINAS - l�nea 75
[005] GENERACI�N DE CONFIG - l�nea 100
[006] CLI                   - l�nea 130
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# [001] IMPORTS / CONFIG
SITE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "BM WEB"))

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}

# Tags que identifican secciones de navegaci�n
NAV_TAGS = ["nav", "header", "menu", "navigation"]
# Tags que identifican contenido principal
MAIN_TAGS = ["main", "article", "section", "div"]
# Selectores CSS comunes de contenido
CONTENT_SELECTORS = [
    "main", "article", ".content", ".post", ".entry",
    ".page-content", "#content", ".main-content",
    "section", ".body", ".post-content", ".entry-content",
]


# [002] ANALIZADOR HTML
class SiteAnalyzer:
    def __init__(self, source):
        self.source = source
        self.soup = None
        self.pages = []
        self.nav_links = []
        self.site_title = ""

    def load(self):
        source_lower = self.source.lower()
        if source_lower.startswith(("http://", "https://")):
            return self._load_url(self.source)
        elif os.path.isdir(self.source):
            return self._load_dir(self.source)
        elif os.path.isfile(self.source):
            return self._load_file(self.source)
        else:
            print(f"Fuente no v�lida: {self.source}")
            return False

    # [003] EXTRACCI�N DE NAV
    def _extract_nav(self):
        if not self.soup:
            return []
        links = set()
        for tag in self.soup.find_all(["a"]):
            href = tag.get("href", "")
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                href = href.split("?")[0].split("#")[0]
                if href:
                    links.add(href)
        return sorted(links)

    def _identify_page_title(self):
        if not self.soup:
            return ""
        title_tag = self.soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            return title_tag.get_text(strip=True)
        h1 = self.soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
        return ""

    # [004] DETECCI�N DE P�GINAS
    def _load_url(self, url):
        if not HAS_BS4:
            print("BeautifulSoup no est� instalado. Ejecuta: pip install beautifulsoup4 lxml")
            return False
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            self.soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print(f"Error al cargar URL: {e}")
            return False
        self.nav_links = self._extract_nav()
        self.site_title = self._identify_page_title()
        self.pages = self._detect_pages()
        return True

    def _load_file(self, filepath):
        if not HAS_BS4:
            print("BeautifulSoup no est� instalado.")
            return False
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                html = f.read()
            self.soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return False
        self.nav_links = self._extract_nav()
        self.site_title = self._identify_page_title()
        self.pages = self._detect_pages_from_file(filepath)
        return True

    def _load_dir(self, directory):
        html_files = sorted(
            Path(directory).rglob("*.html")
        )
        if not html_files:
            print(f"No se encontraron archivos HTML en: {directory}")
            return False
        if not HAS_BS4:
            print("BeautifulSoup no est� instalado.")
            return False
        self.soup = None
        self.pages = []
        seen_files = set()
        for hp in html_files:
            rel = str(hp.relative_to(directory))
            if rel in seen_files:
                continue
            seen_files.add(rel)
            try:
                with open(hp, "r", encoding="utf-8", errors="replace") as f:
                    html = f.read()
                page_soup = BeautifulSoup(html, "html.parser")
                title_tag = page_soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else rel
                self.pages.append({
                    "file": rel,
                    "label": title,
                    "tab_type": self._guess_tab_type(rel, page_soup),
                    "fields": self._guess_fields(page_soup),
                })
            except Exception as e:
                print(f"  Error analizando {rel}: {e}")
        self.site_title = Path(directory).name.replace("_", " ").title()
        return True

    def _detect_pages(self):
        pages = []
        seen = set()
        for link in self.nav_links:
            if link in seen:
                continue
            seen.add(link)
            label = self._label_from_link(link)
            tab_type = self._guess_tab_type(link, self.soup)
            fields = ["title", "body"]
            pages.append({
                "file": link,
                "label": label,
                "tab_type": tab_type,
                "fields": fields,
            })
        if not pages:
            pages.append({
                "file": "index.html",
                "label": "Inicio",
                "tab_type": "content",
                "fields": ["title", "body"],
            })
        return pages

    def _detect_pages_from_file(self, filepath):
        filename = os.path.basename(filepath)
        label = os.path.splitext(filename)[0].replace("_", " ").title()
        tab_type = self._guess_tab_type(filename, self.soup)
        return [{
            "file": filename,
            "label": label,
            "tab_type": tab_type,
            "fields": self._guess_fields(self.soup),
        }]

    def _label_from_link(self, link):
        name = os.path.splitext(os.path.basename(link))[0]
        name = name.replace("-", " ").replace("_", " ")
        return name.title() if name else "P�gina"

    # [005] GENERACI�N DE CONFIG
    def _guess_tab_type(self, path_or_name, soup=None):
        name = os.path.basename(path_or_name).lower() if path_or_name else ""
        if name in ("index.html", "index.htm"):
            return "content"
        if "contact" in name:
            return "contact"
        if "news" in name or "blog" in name or "noticia" in name or "post" in name:
            return "news"
        if "photo" in name or "gallery" in name or "imagen" in name:
            return "photo"
        return "content"

    def _guess_fields(self, soup):
        fields = ["title", "body"]
        if not soup:
            return fields
        forms = soup.find_all("form")
        for form in forms:
            inputs = form.find_all(["input", "textarea"])
            for inp in inputs:
                name = inp.get("name", "").lower()
                itype = inp.get("type", "text").lower()
                if itype == "email" and "email" not in fields:
                    fields.append("email")
                elif itype == "tel" and "phone" not in fields:
                    fields.append("phone")
                elif itype == "text" and name in ("email", "email"):
                    fields.append("email")
                elif itype == "text" and name in ("phone", "tel", "telefono"):
                    fields.append("phone")
        imgs = soup.find_all("img")
        if imgs and "thumb" not in fields and "image" not in fields:
            fields.append("thumb")
        return fields

    def generate_config(self, output_path=None):
        site_name = self.site_title or "Nuevo Sitio"
        config = {
            "site_name": site_name,
            "site_title": site_name,
            "site_root": ".",
            "pages": self.pages,
            "assets_dirs": ["assets/css", "assets/js", "assets/img"],
            "css_file": "assets/css/styles.css",
            "js_file": "assets/js/main.js",
            "generated_by": "site_analyzer",
            "generated_at": datetime.now().isoformat(),
            "source": self.source,
        }
        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        return config

    def summary(self):
        lines = [f"Sitio: {self.site_title or 'Sin t\u00edtulo'}", f"Fuente: {self.source}", f"P�ginas detectadas: {len(self.pages)}", ""]
        for p in self.pages:
            lines.append(f"  {p['file']:30s} [{p['tab_type']:10s}] {p['label']}")
        return "\n".join(lines)


# [006] CLI
def main():
    print("=" * 50)
    print("  Analizador de sitios web")
    print("=" * 50)

    if len(sys.argv) < 2:
        source = input("URL o carpeta/directorio de HTML: ").strip()
    else:
        source = sys.argv[1]

    if not source:
        print("Debe indicar una URL o directorio.")
        sys.exit(1)

    analyzer = SiteAnalyzer(source)
    if not analyzer.load():
        sys.exit(1)

    print()
    print(analyzer.summary())

    output = input("\nArchivo de destino para site_config.json (Enter = site_config.json): ").strip()
    output = output or "site_config.json"

    config = analyzer.generate_config(output)
    print(f"\nConfig generado: {output}")
    print("Puedes abrir el editor ahora para editar el sitio.")


if __name__ == "__main__":
    main()
