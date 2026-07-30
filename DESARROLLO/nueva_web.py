"""
CONTEXTO: Utilidad para crear un nuevo sitio web desde la plantilla.
          Genera site_config.json, HTML iniciales y estructura de assets.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONFIG      - línea 12
[002] CREATER SITE          - línea 20
[003] PAGE GENERATION       - línea 60
[004] MAIN                  - línea 100
"""
import json
import os
import shutil
import sys

# [001] IMPORTS / CONFIG
TEMPLATE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "site_template"))
SITE_ROOT = os.path.join(os.path.dirname(__file__), "..")

DEFAULT_PAGES = [
    {"file": "index.html", "label": "Inicio", "tab_type": "content", "fields": ["title", "body"]},
    {"file": "about.html", "label": "Nosotros", "tab_type": "content", "fields": ["title", "body"]},
    {"file": "contact.html", "label": "Contacto", "tab_type": "contact", "fields": ["email", "phone", "address"]},
    {"file": "news.html", "label": "Noticias", "tab_type": "news", "fields": ["title", "date", "body", "thumb"]},
]

# [002] CREATE SITE
def crear_sitio(site_name, site_root, pages):
    os.makedirs(site_root, exist_ok=True)

    config = {
        "site_name": site_name,
        "site_title": site_name,
        "site_root": ".",
        "pages": pages,
        "assets_dirs": ["assets/css", "assets/js", "assets/img"],
        "css_file": "assets/css/styles.css",
        "js_file": "assets/js/main.js",
    }

    config_path = os.path.join(site_root, "site_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    assets_dirs = config.get("assets_dirs", [])
    for d in assets_dirs:
        os.makedirs(os.path.join(site_root, d), exist_ok=True)

    css_src = os.path.join(TEMPLATE_DIR, "assets", "css", "styles.css")
    css_dst = os.path.join(site_root, config["css_file"])
    if os.path.exists(css_src):
        shutil.copy2(css_src, css_dst)

    for page in pages:
        html_path = os.path.join(site_root, page["file"])
        if not os.path.exists(html_path):
            html = _generar_html(page, config)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)

    js_path = os.path.join(site_root, config["js_file"])
    if not os.path.exists(js_path):
        with open(js_path, "w", encoding="utf-8") as f:
            f.write("// JS inicial\n")

    return config_path


# [003] PAGE GENERATION
def _generar_html(page, config):
    title = page.get("label", page["file"])
    nav_links = "\n".join(
        f'        <a href="{p["file"]}">{p["label"]}</a>' for p in config["pages"]
    )
    fields = page.get("fields", ["title", "body"])

    body_sections = []
    body_sections.append(f'    <h2>{title}</h2>')
    if "body" in fields:
        body_sections.append('    <div class="page-content">')
        body_sections.append('      <p>Contenido aqu&iacute;.</p>')
        body_sections.append('    </div>')
    if "thumb" in fields:
        body_sections.append('    <div class="page-thumb">')
        body_sections.append('      <!-- Agrega imagen aqu&iacute; -->')
        body_sections.append('    </div>')
    if "email" in fields or "phone" in fields or "address" in fields:
        body_sections.append('    <div class="contact-info">')
        if "email" in fields:
            body_sections.append('      <p>Email: <a href="mailto:info@example.com">info@example.com</a></p>')
        if "phone" in fields:
            body_sections.append('      <p>Tel&eacute;fono: +54 9 11 1234-5678</p>')
        if "address" in fields:
            body_sections.append('      <p>Direcci&oacute;n: Ciudad, Pa&iacute;s</p>')
        body_sections.append('    </div>')

    body_html = "\n".join(body_sections)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{config['site_title']} — {title}</title>
<link rel="stylesheet" href="{config['css_file']}">
</head>
<body>
<header>
  <h1>{config['site_title']}</h1>
  <nav>
{nav_links}
  </nav>
</header>
<main>
{body_html}
</main>
<footer>
  <p class="site-footer__version">v1.0 · DD de mes, AAAA</p>
</footer>
</body>
</html>"""


# [004] MAIN
def main():
    print("=" * 50)
    print("  Nuevo Sitio Web — Asistente de creaci\u00f3n")
    print("=" * 50)

    site_name = input("Nombre del sitio: ").strip()
    if not site_name:
        print("El nombre no puede estar vac\u00edo.")
        sys.exit(1)

    default_root = os.path.join(SITE_ROOT, site_name.replace(" ", "_").lower())
    root_input = input(f"Carpeta de destino [{default_root}]: ").strip()
    site_root = os.path.abspath(root_input) if root_input else default_root

    print("\nP\u00e1ginas por defecto:")
    for i, p in enumerate(DEFAULT_PAGES, 1):
        print(f"  {i}. {p['file']} ({p['label']})")

    use_default = input("\u00bfUsar estas p\u00e1ginas? [S/n] ").strip().lower()
    if use_default in ("n", "no"):
        pages = []
        while True:
            file_name = input("Archivo HTML (o 'fin' para terminar): ").strip()
            if file_name.lower() == "fin":
                break
            if not file_name.endswith(".html"):
                file_name += ".html"
            label = input("Etiqueta del men\u00fa: ").strip()
            tab_type = input("Tipo de tab (content/contact/news/photo) [content]: ").strip() or "content"
            fields_str = input("Campos separados por coma (title,body,thumb,email): ").strip()
            fields = [f.strip() for f in fields_str.split(",")] if fields_str else ["title", "body"]
            pages.append({
                "file": file_name,
                "label": label or file_name,
                "tab_type": tab_type,
                "fields": fields,
            })
    else:
        pages = DEFAULT_PAGES

    config_path = crear_sitio(site_name, site_root, pages)
    print(f"\nSitio creado en: {site_root}")
    print(f"Config: {config_path}")
    print("\nPara editar con el editor, abre el editor y selecciona esta carpeta.")


if __name__ == "__main__":
    main()
