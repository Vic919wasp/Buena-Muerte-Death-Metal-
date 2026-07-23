"""
CONTEXTO: Constructor de prompts para Ollama. Arma el contexto completo
          con info de la banda, escena ARG y datos del evento para que
          la AI genere textos relevantes y acertados.
ÍNDICE DE NAVEGACIÓN
[001] INFO BANDA              - línea 12
[002] CONTEXTOS               - línea 35
[003] BUILDERS DE PROMPT      - línea 60
[004] PLANTILLAS              - línea 120
"""
import json
from typing import Optional

# [001] INFO BANDA
BAND_INFO = {
    "nombre": "Buena Muerte",
    "genero": "Death Metal",
    "zona": "Zona Sur, AMBA, Argentina",
    "origen": "Buenos Aires, Argentina",
    "anio": "2013",
    "whatsapp": "5491164377706",
    "cantante": "Favio Leguizamón",
    "sello": "Macabre Records",
    "redes": {
        "web": "buena-muerte-death-metal.onrender.com",
        "spotify": "open.spotify.com/artist/5q9MTB7bYNx20VzAsYTblL",
        "instagram": "instagram.com/buena.muerte",
        "youtube": "youtube.com/results?search_query=buena+muerte+death+metal",
    },
}


# [002] CONTEXTOS
def build_band_context() -> str:
    """Arma contexto descriptivo de la banda."""
    return (
        f"La banda se llama {BAND_INFO['nombre']}, tocan {BAND_INFO['genero']}. "
        f"Son de {BAND_INFO['zona']}, formada en {BAND_INFO['anio']}. "
        f"El cantante es {BAND_INFO['cantante']}. "
        f"El sello es {BAND_INFO['sello']}. "
        f"Ventas de entradas por WhatsApp: {BAND_INFO['whatsapp']}. "
        f"Sitio: {BAND_INFO['redes']['web']}"
    )


def build_scene_context(scene_data: Optional[dict] = None) -> str:
    """Arma contexto de la escena metal ARG (máx 300 chars)."""
    if not scene_data:
        return "Contexto de escena no disponible."
    lines = ["Escena metal argentina actual:"]
    if scene_data.get("shows"):
        lines.append("Shows confirmados en Buenos Aires:")
        for s in scene_data["shows"][:5]:
            fecha = s.get("fecha", "")
            lugar = s.get("lugar", s.get("titulo", ""))
            lines.append(f"  - {fecha} en {lugar}")
    if scene_data.get("noticias"):
        lines.append("Noticias recientes:")
        for n in scene_data["noticias"][:3]:
            lines.append(f"  - {n.get('titulo', '')}")
    return "\n".join(lines)[:300]


# [003] BUILDERS DE PROMPT
def build_improve_description_prompt(event: dict, scene_data: Optional[dict] = None) -> list:
    """Prompt para mejorar la descripción de una fecha de tour."""
    band_ctx = build_band_context()
    scene_ctx = build_scene_context(scene_data) if scene_data else ""
    event_str = json.dumps(event, ensure_ascii=False, indent=2)

    system = (
        f"Sos el redactor de {BAND_INFO['nombre']}, banda de {BAND_INFO['genero']} "
        f"de {BAND_INFO['zona']}. Generá una descripción para un show de la banda.\n"
        f"Estilo: underground, directo, pasional, argentino. "
        f"Emojis de metal: 🤘🔥💀🎸🥁. 2-4 oraciones máximo. "
        f"Incluí fecha, lugar, bandas invitadas si las hay. "
        f"CTA: WhatsApp {BAND_INFO['whatsapp']}. "
        f"No inventes info. Death metal, no heavy ni rock. "
        f"DATOS: {band_ctx}"
    )

    user_msg = f"Generá la descripción para este show:\n\n{event_str}"
    if scene_ctx:
        user_msg += f"\n\nCONTEXTO DE LA ESCENA ARG:\n{scene_ctx}"

    return [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]


def build_improve_existing_prompt(text: str, event: dict = None,
                                   scene_data: Optional[dict] = None) -> list:
    """Prompt para mejorar un texto existente."""
    band_ctx = build_band_context()
    scene_ctx = build_scene_context(scene_data) if scene_data else ""
    event_str = json.dumps(event, ensure_ascii=False, indent=2) if event else ""

    system = (
        f"Sos el community manager de {BAND_INFO['nombre']}, "
        f"{BAND_INFO['genero']} de {BAND_INFO['zona']}. "
        f"Mejorá el texto dado para que sea más impactante y profesional, "
        f"manteniendo el tono underground argentino. "
        f"Reglas: mantené la info correcta, mejorá gramática, "
        f"hacelo más atractivo para la escena metal, longitud similar al original. "
        f"DATOS: {band_ctx}"
    )

    user_msg = f"Mejorá este texto:\n\n---\n{text}\n---"
    if event_str:
        user_msg += f"\n\nDATOS DEL EVENTO:\n{event_str}"
    if scene_ctx:
        user_msg += f"\n\n{scene_ctx}"
    user_msg += "\n\nVersión mejorada:"

    return [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]


def build_generate_post_prompt(event: dict, scene_data: Optional[dict] = None) -> list:
    """Prompt para generar un post de redes sociales."""
    band_ctx = build_band_context()
    scene_ctx = build_scene_context(scene_data) if scene_data else ""
    event_str = json.dumps(event, ensure_ascii=False, indent=2)

    system = (
        f"Sos el community manager de {BAND_INFO['nombre']}, "
        f"{BAND_INFO['genero']} de {BAND_INFO['zona']}. "
        f"Generá un post para Instagram/Facebook sobre un show.\n"
        f"Estilo: underground, directo, argentino. "
        f"Emojis: 🤘🔥💀🎸🥁. Hashtags: #BuenaMuerte #DeathMetal #MetalArgentino. "
        f"4-8 oraciones. Incluí fecha, lugar, cómo entrar. "
        f"CTA: WhatsApp {BAND_INFO['whatsapp']}. "
        f"DATOS: {band_ctx}"
    )

    user_msg = f"Generá el post para este show:\n\n{event_str}"
    if scene_ctx:
        user_msg += f"\n\nESCENA ARG:\n{scene_ctx}"

    return [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]


def build_quick_prompt(user_input: str, context: str = "") -> list:
    """Prompt rápido para consultas generales sobre la banda."""
    band_ctx = build_band_context()
    system = (
        f"Sos el asistente de {BAND_INFO['nombre']}, {BAND_INFO['genero']} "
        f"de {BAND_INFO['zona']}. Respondé en español, sé conciso. "
        f"INFO: {band_ctx}"
    )
    if context:
        system += f"\n\nCONTEXTO ADICIONAL:\n{context}"

    return [{"role": "system", "content": system}, {"role": "user", "content": user_input}]


# [004] PLANTILLAS
PLANTILLAS_DESCRIPCION = {
    "basica": (
        "{lugar} — {ciudad}\n"
        "{dia} de {mes}\n"
        "{descripcion}\n"
        "🎫 Entradas: wa.me/{whatsapp}"
    ),
    "redes": (
        "🤘 *{lugar}* 🤘\n"
        "📍 {ciudad} | 📅 {dia}/{mes}/{anio}\n"
        "{descripcion}\n"
        "🔥 No te lo pierdas!\n"
        "🎫 wa.me/{whatsapp}"
    ),
}
