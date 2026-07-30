"""
CONTEXTO: Estado del proyecto Buena Muerte — sitio web + editor desktop.
          Última actualización: 2026-07-23
ÍNDICE DE NAVEGACIÓN
[001] ESTADO GENERAL           - línea 12
[002] SITIO WEB                 - línea 20
[003] EDITOR DESKTOP            - línea 35
[004] INTELIGENCIA ARTIFICIAL   - línea 50
[005] PENDIENTES                - línea 70
"""
# [001] ESTADO GENERAL
ESTADO = {
    "proyecto": "Buena Muerte — Death Metal, Zona Sur, AMBA",
    "version_sitio": "v1.10",
    "version_editor": "v1.10",
    "ultima_actualizacion": "2026-07-23",
    "estado": "Activo — en desarrollo",
}

# [002] SITIO WEB
SITIO = {
    "url": "https://buena-muerte-death-metal.onrender.com",
    "tecnologia": "HTML/CSS/JS estático + Flask backend",
    "hosting": "Render.com (free tier)",
    "archivos_principales": [
        "index.html — Página principal",
        "tour.html — Fechas y shows",
        "discography.html — Discografía",
        "news.html — Noticias",
        "band.html — La banda",
        "contact.html — Contacto",
        "video.html — Videos",
        "newsletter.html — Newsletter",
        "admin.html — Panel admin",
        "404.html — Página de error",
    ],
    "assets": [
        "assets/css.css — Estilos (Cinzel/Inter, dark theme)",
        "assets/js.js — Lógica (fechas, share, rendering)",
    ],
    "features": [
        "Responsive (mobile-first)",
        "Share flyers (Web Share API + WhatsApp)",
        "SEO (Open Graph, sitemap, robots.txt)",
        "Favicon y manifest",
        "Lazy loading de imágenes",
        "404 personalizado",
    ],
    "backend": {
        "tecnologia": "Flask (Python)",
        "archivos": ["backend/app.py", "backend/requirements.txt"],
        "endpoints": ["/api/newsletter", "/api/visits"],
    },
}

# [003] EDITOR DESKTOP
EDITOR = {
    "tecnologia": "PySide6 (Qt for Python)",
    "ubicacion": "DESARROLLO/editor/",
    "archivos_principales": [
        "main.py — Ventana principal (9 tabs)",
        "config.py — Configuración general",
        "tabs/ai_tab.py — Asistente AI con router local/cloud",
        "tabs/content_tab.py — Pipeline de contenido",
        "tabs/site_tab.py — Publicación del sitio",
    ],
    "servicios": [
        "services/ai_service.py — Cliente Ollama (local)",
        "services/openrouter_service.py — Cliente OpenRouter (cloud, 3 modelos free)",
        "services/gemini_service.py — Cliente Gemini (cloud, pendiente configuración)",
        "services/ai_router.py — Router inteligente local↔cloud",
        "services/scraper.py — Scraper de escena metal ARG",
        "services/content_scraper.py — Scraper de contenido periodístico",
        "services/file_handler.py — Manejador de archivos adjuntos",
        "services/prompt_builder.py — Constructor de prompts",
        "services/news_generator.py — Generador de noticias",
        "services/site_publisher.py — Publicación del sitio",
    ],
    "features": [
        "9 tabs: Sitio, Noticias, Fechas, Discografía, Media, Newsletter, AI, Pipeline, Publicar",
        "Router IA: tareas livianas → Ollama local, pesadas → OpenRouter cloud",
        "Adjuntos: imágenes (OCR), video (metadata), audio, documentos",
        "Scraping de escena ARG con cache 6h",
        "Publicación con git push a Render",
        "Token tracking (diario/semanal/mensual)",
        "Acciones rápidas editables",
    ],
}

# [004] INTELIGENCIA ARTIFICIAL
AI = {
    "backends": {
        "openrouter": {
            "estado": "Activo y funcionando",
            "key": "sk-or-v1-5ca7... (guardada en editor_config.json)",
            "modelos_free": [
                "nvidia/nemotron-nano-9b-v2:free (default)",
                "openai/gpt-oss-20b:free",
                "nvidia/nemotron-nano-12b-v2-vl:free",
            ],
            "retry": "Automático entre modelos si 429",
        },
        "ollama": {
            "estado": "Disponible (local)",
            "modelos": ["llama3.2:3b", "qwen2.5:1.5b"],
            "nota": "Lento en PC de desarrollo, usado para tareas livianas",
        },
        "gemini": {
            "estado": "Pendiente — key con rate limit 0",
            "key": "AQ.Ab8RN6K... (guardada, no funcional)",
            "nota": "Requiere habilitar Generative Language API en Google Cloud",
        },
    },
    "router": {
        "tareas_locales": ["classify", "summarize", "token_count", "preview", "autocomplete"],
        "tareas_cloud": ["generate", "improve", "analyze", "code"],
    },
    "prompt_periodistico": {
        "estilo": "Brave Words / Metal Injection / Decibel",
        "reglas": [
            "SOLO información del contexto scrapeado",
            "Estructura: nombre → rol → datos confirmados → fuentes",
            "Sin humo ("gran bajista", "mucha experiencia")",
            "Citar fuentes entre paréntesis",
        ],
    },
}

# [005] PENDIENTES
PENDIENTES = [
    "Habilitar Gemini (configurar Google Cloud API)",
    "Agregar más fuentes de scraping (Metal Archives, SAMetalIndex)",
    "Mejorar extracción de frames de video",
    "OCR con Tesseract (instalar pytesseract + Pillow)",
    "Integrar PyMuPDF para PDFs",
    "Tests unitarios",
    "Documentación de uso del editor",
]
