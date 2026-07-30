"""
CONTEXTO: Manejador de archivos adjuntos — detecta tipo, extrae
          contenido (OCR, metadata, texto) para pasar a la AI.
ÍNDICE DE NAVEGACIÓN
[001] CONFIG / TIPOS           - línea 12
[002] DETECCIÓN                - línea 25
[003] EXTRACCIÓN IMAGEN (OCR)  - línea 40
[004] EXTRACCIÓN DOCUMENTO     - línea 70
[005] EXTRACCIÓN VIDEO/AUDIO   - línea 95
[006] FUNCIÓN PRINCIPAL        - línea 120
"""
import os
import json
import subprocess
import tempfile
from typing import Optional

# [001] CONFIG
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}
DOC_EXTS = {".pdf", ".doc", ".docx", ".txt", ".md", ".csv", ".json"}

# [002] DETECCIÓN
def detect_file_type(filepath: str) -> str:
    """Retorna: 'image', 'video', 'audio', 'document', 'unknown'"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in DOC_EXTS:
        return "document"
    return "unknown"


def get_file_info(filepath: str) -> dict:
    """Retorna info básica del archivo."""
    name = os.path.basename(filepath)
    size = os.path.getsize(filepath)
    ftype = detect_file_type(filepath)
    return {
        "name": name,
        "path": filepath,
        "type": ftype,
        "size": size,
        "size_human": _human_size(size),
        "ext": os.path.splitext(filepath)[1].lower(),
    }


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# [003] EXTRACCIÓN IMAGEN (OCR)
def extract_image_text(filepath: str) -> str:
    """Extrae texto de imagen via Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang="spa+eng")
        return text.strip()
    except ImportError:
        return "[OCR no disponible — instalar pytesseract y Pillow]"
    except Exception as e:
        return f"[Error OCR: {e}]"


def extract_image_metadata(filepath: str) -> dict:
    """Extrae metadata EXIF de imagen."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(filepath)
        meta = {"dimensions": f"{img.width}x{img.height}", "format": img.format}
        exif = img.getexif()
        if exif:
            for tag_id, val in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if isinstance(tag, str) and tag in ("DateTime", "Make", "Model", "Software"):
                    meta[tag] = str(val)
        return meta
    except Exception:
        return {"dimensions": "unknown"}


# [004] EXTRACCIÓN DOCUMENTO
def extract_document_text(filepath: str) -> str:
    """Extrae texto de documentos."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt" or ext == ".md":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()[:5000]

    if ext == ".json":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        return json.dumps(data, ensure_ascii=False, indent=2)[:5000]

    if ext == ".csv":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[:50]
        return "".join(lines)

    if ext == ".pdf":
        return _extract_pdf(filepath)

    if ext in (".doc", ".docx"):
        return _extract_docx(filepath)

    return f"[Tipo {ext} no soportado para extracción de texto]"


def _extract_pdf(filepath: str) -> str:
    """Extrae texto de PDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(filepath)
        text = ""
        for page in doc[:10]:
            text += page.get_text()
        doc.close()
        return text[:5000]
    except ImportError:
        pass

    try:
        result = subprocess.run(
            ["pdftotext", filepath, "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout[:5000]
    except Exception:
        pass

    return "[PDF: instalar PyMuPDF (pip install pymupdf) o pdftotext]"


def _extract_docx(filepath: str) -> str:
    """Extrae texto de DOCX."""
    try:
        from docx import Document
        doc = Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs[:100]])
        return text[:5000]
    except ImportError:
        return "[DOCX: instalar python-docx (pip install python-docx)]"
    except Exception as e:
        return f"[Error DOCX: {e}]"


# [005] EXTRACCIÓN VIDEO/AUDIO
def extract_media_metadata(filepath: str) -> dict:
    """Extrae metadata de video/audio via ffprobe."""
    meta = {"filename": os.path.basename(filepath), "size": _human_size(os.path.getsize(filepath))}

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            fmt = data.get("format", {})
            if fmt.get("duration"):
                meta["duration"] = f"{float(fmt['duration']):.1f}s"
            if fmt.get("bit_rate"):
                meta["bitrate"] = f"{int(fmt['bit_rate'])//1000}kbps"

            streams = data.get("streams", [])
            for s in streams:
                if s.get("codec_type") == "video":
                    meta["video"] = f"{s.get('codec_name')} {s.get('width')}x{s.get('height')}"
                elif s.get("codec_type") == "audio":
                    meta["audio"] = f"{s.get('codec_name')} {s.get('sample_rate')}Hz"
    except FileNotFoundError:
        meta["note"] = "ffprobe no encontrado — instalar ffmpeg"
    except Exception:
        pass

    return meta


def extract_video_frame(filepath: str) -> Optional[str]:
    """Extrae un frame del video para preview."""
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.close()
        subprocess.run(
            ["ffmpeg", "-y", "-i", filepath, "-ss", "00:00:01", "-vframes", "1", tmp.name],
            capture_output=True, timeout=30
        )
        if os.path.getsize(tmp.name) > 0:
            return tmp.name
        os.unlink(tmp.name)
    except Exception:
        pass
    return None


# [006] FUNCIÓN PRINCIPAL
def process_attachment(filepath: str) -> dict:
    """
    Procesa un archivo adjunto y retorna info + contenido extraído.
    Retorna: {info: dict, content: str, preview_path: str|None}
    """
    info = get_file_info(filepath)
    content = ""
    preview_path = None

    if info["type"] == "image":
        content = extract_image_text(filepath)
        meta = extract_image_metadata(filepath)
        info["meta"] = meta
        preview_path = filepath

    elif info["type"] == "document":
        content = extract_document_text(filepath)

    elif info["type"] == "video":
        meta = extract_media_metadata(filepath)
        info["meta"] = meta
        preview_path = extract_video_frame(filepath)

    elif info["type"] == "audio":
        meta = extract_media_metadata(filepath)
        info["meta"] = meta

    return {
        "info": info,
        "content": content,
        "preview_path": preview_path,
    }
