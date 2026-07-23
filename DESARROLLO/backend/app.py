"""
CONTEXTO: Backend mínimo Flask para newsletter y contador de visitas
          del sitio Buena Muerte. SQLite WAL, CORS para localhost.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONFIG      - línea 12
[002] RUTAS NEWSLETTER      - línea 25
[003] RUTAS VISITAS         - línea 55
[004] MAIN                  - línea 70
"""
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# [001] IMPORTS / CONFIG
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:*", "http://localhost:*"])

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "buena_muerte.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            count INTEGER DEFAULT 0,
            updated TEXT DEFAULT (datetime('now'))
        );
        INSERT OR IGNORE INTO visits (id, count) VALUES (1, 0);
    """)
    db.commit()
    db.close()


# [002] RUTAS NEWSLETTER
@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json(silent=True)
    if not data or not data.get("email"):
        return jsonify({"error": "Email requerido"}), 400
    email = data["email"].strip().lower()
    if "@" not in email or "." not in email:
        return jsonify({"error": "Email inválido"}), 400
    db = get_db()
    try:
        db.execute(
            "INSERT INTO subscribers (email) VALUES (?)",
            (email,),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Ya está suscripto"}), 409
    return jsonify({"ok": True, "email": email}), 201


@app.route("/api/subscribers", methods=["GET"])
def list_subscribers():
    db = get_db()
    rows = db.execute(
        "SELECT id, email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/subscribers/<int:sid>", methods=["DELETE"])
def delete_subscriber(sid):
    db = get_db()
    db.execute("DELETE FROM subscribers WHERE id = ?", (sid,))
    db.commit()
    return jsonify({"ok": True})


# [003] RUTAS VISITAS
@app.route("/api/visit", methods=["POST"])
def increment_visit():
    db = get_db()
    db.execute(
        "UPDATE visits SET count = count + 1, updated = datetime('now') WHERE id = 1"
    )
    db.commit()
    row = db.execute("SELECT count FROM visits WHERE id = 1").fetchone()
    return jsonify({"visits": row["count"]})


@app.route("/api/visits", methods=["GET"])
def get_visits():
    db = get_db()
    row = db.execute("SELECT count FROM visits WHERE id = 1").fetchone()
    return jsonify({"visits": row["count"]})


# [004] MAIN
if __name__ == "__main__":
    init_db()
    print("Backend Buena Muerte corriendo en http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
