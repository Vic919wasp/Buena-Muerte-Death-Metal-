"""
CONTEXTO: Publicador del sitio — ejecuta git add/commit/push para
          subir cambios a Render.com.
ÍNDICE DE NAVEGACIÓN
[001] CONFIG                - línea 11
[002] PUBLICAR              - línea 18
"""
import os
import subprocess
from datetime import datetime

# [001] CONFIG
SITE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _run(cmd, cwd=SITE_ROOT):
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, timeout=30
    )
    out = result.stdout.decode("utf-8", errors="replace").strip() if result.stdout else ""
    err = result.stderr.decode("utf-8", errors="replace").strip() if result.stderr else ""
    return result.returncode == 0, out, err


# [002] PUBLICAR
def publish(message=None):
    ok, out, err = _run("git status --porcelain")
    if not ok:
        return False, f"Error al leer estado git: {err}"

    if not out.strip():
        return True, "No hay cambios para publicar."

    msg = message or f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    steps = [
        ("git add -A", "Stage de archivos"),
        f'git commit -m "{msg}"', "Commit",
        "git push", "Push a Render",
    ]

    for cmd, desc in steps:
        ok, out, err = _run(cmd)
        if not ok:
            return False, f"Error en {desc}: {err}"

    return True, "Sitio publicado correctamente."


def get_status():
    ok, out, err = _run("git status --porcelain")
    if not ok:
        return {"error": err}
    lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
    return {"changed": len(lines), "files": lines}


def get_log(n=5):
    ok, out, err = _run(f"git log --oneline -{n}")
    if not ok:
        return []
    return [l.strip() for l in out.strip().split("\n") if l.strip()]
