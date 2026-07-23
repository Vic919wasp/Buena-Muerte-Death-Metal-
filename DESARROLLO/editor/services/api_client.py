"""
CONTEXTO: Cliente HTTP para comunicar el editor con el backend Flask
          de Buena Muerte (newsletter + visitas).
ÍNDICE DE NAVEGACIÓN
[001] CONFIG                - línea 11
[002] NEWSLETTER            - línea 18
[003] VISITAS               - línea 38
"""
import json
import urllib.request
import urllib.error

# [001] CONFIG
DEFAULT_API = "http://127.0.0.1:5000"


def _request(method, path, data=None, api_base=DEFAULT_API):
    url = api_base.rstrip("/") + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError:
        return None
    except Exception:
        return None


# [002] NEWSLETTER
def subscribe(email, api_base=DEFAULT_API):
    return _request("POST", "/api/subscribe", {"email": email}, api_base)


def list_subscribers(api_base=DEFAULT_API):
    return _request("GET", "/api/subscribers", api_base=api_base)


def delete_subscriber(sid, api_base=DEFAULT_API):
    return _request("DELETE", f"/api/subscribers/{sid}", api_base=api_base)


# [003] VISITAS
def get_visits(api_base=DEFAULT_API):
    return _request("GET", "/api/visits", api_base=api_base)


def increment_visit(api_base=DEFAULT_API):
    return _request("POST", "/api/visit", api_base=api_base)
