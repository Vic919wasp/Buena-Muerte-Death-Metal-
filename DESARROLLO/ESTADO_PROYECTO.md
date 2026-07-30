# Estado del Proyecto — Buena Muerte

**Última actualización:** 2026-07-23  
**Versión sitio:** v1.10 | **Versión editor:** v1.10

---

## Sitio Web

| Item | Detalle |
|------|---------|
| URL | https://buena-muerte-death-metal.onrender.com |
| Tech | HTML/CSS/JS estático + Flask backend |
| Hosting | Render.com (free tier) |

**Archivos:**
- `index.html` — Principal
- `tour.html` — Fechas y shows
- `discography.html` — Discografía
- `news.html` — Noticias
- `band.html` — La banda
- `contact.html` — Contacto
- `video.html` — Videos
- `admin.html` — Panel admin
- `404.html` — Error personalizado

**Features:** Responsive, Share flyers, SEO (OG, sitemap, robots), Favicon, Lazy loading

---

## Editor Desktop

| Item | Detalle |
|------|---------|
| Tech | PySide6 (Qt for Python) |
| Ubicación | `DESARROLLO/editor/` |
| Tabs | 9: Sitio, Noticias, Fechas, Discografía, Media, Newsletter, AI, Pipeline, Publicar |

**Servicios:**
- `ai_service.py` — Ollama (local)
- `openrouter_service.py` — OpenRouter (cloud, 3 modelos free)
- `ai_router.py` — Router inteligente local↔cloud
- `scraper.py` — Escena metal ARG (cache 6h)
- `content_scraper.py` — Scraper periodístico
- `file_handler.py` — Adjuntos (imagen/video/audio/doc)
- `site_publisher.py` — Publicación git push

---

## Inteligencia Artificial

### Backends

| Backend | Estado | Modelos |
|---------|--------|---------|
| **OpenRouter** | ✅ Activo | Nemotron Nano 9B, GPT-OSS 20B, Nemotron 12B VL |
| **Ollama** | ✅ Local | llama3.2:3b, qwen2.5:1.5b |
| **Gemini** | ⏳ Pendiente | Requiere habilitar API en Google Cloud |

### Router Inteligente

- **Tareas livianas → Ollama local:** clasificar, resumir, preview, token count, autocomplete
- **Tareas pesadas → OpenRouter cloud:** generar, mejorar, analizar, código

### Prompt Periodístico

- Estilo: Brave Words / Metal Injection / Decibel
- Solo información del contexto scrapeado
- Estructura: nombre → rol → datos confirmados → fuentes
- Sin humo, con citas entre paréntesis

---

## Pendientes

1. [ ] Habilitar Gemini (configurar Google Cloud API)
2. [ ] Agregar más fuentes de scraping (Metal Archives, SAMetalIndex)
3. [ ] Mejorar extracción de frames de video
4. [ ] OCR con Tesseract (instalar pytesseract + Pillow)
5. [ ] Integrar PyMuPDF para PDFs
6. [ ] Tests unitarios
7. [ ] Documentación de uso del editor

---

## Archivos Clave

```
DESARROLLO/
├── index.html, tour.html, discography.html, ...  ← Sitio estático
├── assets/css.css, js.js                          ← Estilos y lógica
├── backend/app.py                                  ← Flask API
├── editor/
│   ├── main.py                                     ← Editor PySide6
│   ├── config.py                                   ← Configuración
│   ├── editor_config.json                          ← API keys
│   ├── tabs/
│   │   ├── ai_tab.py                               ← Chat IA con router
│   │   ├── content_tab.py                          ← Pipeline de contenido
│   │   └── ...
│   └── services/
│       ├── ai_service.py                           ← Ollama
│       ├── openrouter_service.py                   ← OpenRouter
│       ├── ai_router.py                            ← Router local↔cloud
│       ├── content_scraper.py                      ← Scraper periodístico
│       ├── file_handler.py                         ← Adjuntos
│       └── ...
└── ENTREGABLE/                                     ← Deployable
```
