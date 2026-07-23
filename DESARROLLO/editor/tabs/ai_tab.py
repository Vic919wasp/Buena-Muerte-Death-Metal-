"""
CONTEXTO: Tab de asistente AI — chat, acciones rápidas editables,
          scraper de escena ARG, análisis de código, historial de tokens.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE        - línea 12
[002] DEFAULT ACTIONS        - línea 32
[003] UI / LAYOUT            - línea 44
[004] ACCIONES AI            - línea 160
[005] CHAT                   - línea 245
[006] ACCIONES RÁPIDAS EDIT  - línea 295
[007] TOKEN HISTORY          - línea 360
[008] HELPERS                - línea 420
"""
import json
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QFrame, QSplitter, QMessageBox,
    QComboBox, QProgressBar, QListWidget, QListWidgetItem,
    QInputDialog, QMenu,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction

from services import ai_service
from services import scraper
from services.prompt_builder import (
    build_improve_description_prompt,
    build_improve_existing_prompt,
    build_generate_post_prompt,
    build_quick_prompt,
    BAND_INFO,
)

ACTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "quick_actions.json")
USAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "token_usage.json")

DEFAULT_ACTIONS = [
    {"label": "Actualizar escena ARG", "prompt": "", "action": "scrape"},
    {"label": "Mejorar descripcion", "prompt": "", "action": "improve_desc"},
    {"label": "Generar post redes", "prompt": "", "action": "gen_post"},
    {"label": "Analizar codigo sitio", "prompt": "", "action": "analyze"},
]


# [001] IMPORTS / CLASE
class AIWorker(QThread):
    """Worker para llamadas a Ollama sin bloquear la UI."""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        try:
            result = ai_service.chat(self.messages)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# [002] DEFAULT ACTIONS

# [003] UI / LAYOUT
class AITab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_data = None
        self.chat_history = []
        self._worker = None
        self._actions = self._load_actions()
        self._action_btns = []
        self._setup_ui()
        self._check_ollama()
        self._refresh_usage_stats()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QLabel("Asistente AI")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        self.status_label = QLabel("Verificando Ollama...")
        self.status_label.setStyleSheet("color:#9aa0a6; font-size:11px;")
        layout.addWidget(self.status_label)

        main_split = QSplitter(Qt.Horizontal)

        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame{border:1px solid #1f2225; padding:8px;}")
        left_l = QVBoxLayout(left_panel)
        left_l.setContentsMargins(6, 6, 6, 6)

        actions_header = QHBoxLayout()
        lbl = QLabel("Acciones rapidas")
        lbl.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif;")
        actions_header.addWidget(lbl)
        add_action_btn = QPushButton("+")
        add_action_btn.setFixedSize(24, 24)
        add_action_btn.setToolTip("Agregar accion rapida")
        add_action_btn.clicked.connect(self._add_action)
        actions_header.addWidget(add_action_btn)
        actions_header.addStretch()
        left_l.addLayout(actions_header)

        self.actions_list = QListWidget()
        self.actions_list.setStyleSheet("QListWidget{border:none; background:transparent;}")
        self.actions_list.itemDoubleClicked.connect(self._edit_action)
        self.actions_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.actions_list.customContextMenuRequested.connect(self._action_context_menu)
        left_l.addWidget(self.actions_list)
        self._refresh_actions_list()

        run_btn = QPushButton("Ejecutar seleccion")
        run_btn.clicked.connect(self._run_selected_action)
        left_l.addWidget(run_btn)

        sep = QLabel("Escena metal ARG")
        sep.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif; margin-top:8px;")
        left_l.addWidget(sep)

        self.scene_text = QTextEdit()
        self.scene_text.setReadOnly(True)
        self.scene_text.setPlaceholderText("Clic en 'Actualizar escena ARG'...")
        self.scene_text.setMaximumHeight(120)
        left_l.addWidget(self.scene_text)

        usage_header = QLabel("Uso de tokens")
        usage_header.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif; margin-top:8px;")
        left_l.addWidget(usage_header)

        self.usage_day = QLabel("Hoy: 0 tokens")
        self.usage_day.setStyleSheet("color:#9aa0a6; font-size:11px;")
        left_l.addWidget(self.usage_day)
        self.usage_week = QLabel("Semana: 0 tokens")
        self.usage_week.setStyleSheet("color:#9aa0a6; font-size:11px;")
        left_l.addWidget(self.usage_week)
        self.usage_month = QLabel("Mes: 0 tokens")
        self.usage_month.setStyleSheet("color:#9aa0a6; font-size:11px;")
        left_l.addWidget(self.usage_month)
        self.usage_total = QLabel("Total: 0 tokens")
        self.usage_total.setStyleSheet("color:#7a6346; font-size:11px; font-weight:bold;")
        left_l.addWidget(self.usage_total)

        left_l.addStretch()

        token_row = QHBoxLayout()
        token_row.addWidget(QLabel("Tokens:"))
        self.token_label = QLabel("0")
        self.token_label.setStyleSheet("color:#7a6346; font-size:10px; min-width:40px;")
        token_row.addWidget(self.token_label)
        token_row.addStretch()
        left_l.addLayout(token_row)

        main_split.addWidget(left_panel)

        right_panel = QWidget()
        right_l = QVBoxLayout(right_panel)
        right_l.setContentsMargins(0, 0, 0, 0)

        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setStyleSheet("QTextEdit{font-family:'Inter',sans-serif; background:#0d0f10; border:1px solid #1f2225; padding:8px;}")
        right_l.addWidget(self.chat_output, 1)

        chat_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribi tu pregunta...")
        self.chat_input.returnPressed.connect(self._send_chat)
        self.chat_input.textChanged.connect(self._update_token_count)
        chat_row.addWidget(self.chat_input, 1)
        self.send_btn = QPushButton("Enviar")
        self.send_btn.clicked.connect(self._send_chat)
        chat_row.addWidget(self.send_btn)
        right_l.addLayout(chat_row)

        main_split.addWidget(right_panel)
        main_split.setSizes([260, 500])
        layout.addWidget(main_split, 1)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar{border:1px solid #1f2225; height:3px;} QProgressBar::chunk{background:#4a0f0d;}")
        layout.addWidget(self.progress)

    # [004] ACCIONES AI
    def _check_ollama(self):
        if ai_service.OllamaClient().is_available():
            self.status_label.setText("Ollama conectado (llama3.2:3b)")
            self.status_label.setStyleSheet("color:#4a9; font-size:11px;")
        else:
            self.status_label.setText("Ollama no detectado. Inicia Ollama para usar el asistente.")
            self.status_label.setStyleSheet("color:#a44; font-size:11px;")

    def _scrape_scene(self):
        self.progress.setVisible(True)
        self.status_label.setText("Scrapeando escena ARG...")

        class ScraperWorker(QThread):
            finished = Signal(dict)
            def run(self):
                try:
                    data = scraper.force_refresh()
                    self.finished.emit(data)
                except Exception:
                    self.finished.emit({"error": "Error al scrapear"})

        worker = ScraperWorker()
        worker.finished.connect(self._on_scene_loaded)
        worker.start()
        self._scraper_worker = worker

    def _on_scene_loaded(self, data):
        self.progress.setVisible(False)
        self.status_label.setText("Ollama conectado (llama3.2:3b)" if ai_service.OllamaClient().is_available() else "Ollama no detectado.")
        if "error" in data:
            self.scene_text.setPlainText(data["error"])
            return
        self.scene_data = data
        summary = scraper.get_scene_summary()
        self.scene_text.setPlainText(summary)

    def _improve_description(self):
        if not self.scene_data:
            QMessageBox.information(self, "Escena", "Primero actualiza la escena ARG.")
            return
        event = {
            "lugar": "EL TEATRITO", "ciudad": "CABA",
            "dia": "27", "mes": "OCT", "anio": "2026",
            "descripcion": "Show de Buena Muerte en El Teatrito",
        }
        self.progress.setVisible(True)
        messages = build_improve_description_prompt(event, self.scene_data)
        self._run_ai(messages, "Mejorando descripcion...")

    def _generate_post(self):
        if not self.scene_data:
            QMessageBox.information(self, "Escena", "Primero actualiza la escena ARG.")
            return
        event = {
            "lugar": "EL TEATRITO", "ciudad": "CABA",
            "dia": "27", "mes": "OCT", "anio": "2026",
            "descripcion": "Buena Muerte + Six Feet Under",
        }
        self.progress.setVisible(True)
        messages = build_generate_post_prompt(event, self.scene_data)
        self._run_ai(messages, "Generando post...")

    def _analyze_code(self):
        self.progress.setVisible(True)
        from services import html_generator
        code = html_generator._read("assets/js.js")[:3000]
        messages = [
            {"role": "system", "content": "Sos experto en Python/JS/PySide6. Analiza codigo y sugiere mejoras. Responde en español, sé conciso."},
            {"role": "user", "content": f"Analiza este codigo:\n\n```\n{code}\n```"},
        ]
        self._run_ai(messages, "Analizando codigo...")

    def _run_custom_action(self, prompt):
        self.progress.setVisible(True)
        ctx = (scraper.get_scene_summary() if self.scene_data else "")[:300]
        messages = build_quick_prompt(prompt, ctx)
        self._run_ai(messages, "Procesando...")

    # [005] CHAT
    def _send_chat(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        text = text[:500]
        self.chat_input.clear()
        self.chat_output.append(f"Tu: {text}\n")
        self.chat_history.append({"role": "user", "content": text})
        ctx = (scraper.get_scene_summary() if self.scene_data else "")[:300]
        system = "Sos asistente de Buena Muerte (death metal, Zona Sur, AMBA). Sé conciso."
        if ctx:
            system += f" Escena ARG: {ctx}"
        messages = [{"role": "system", "content": system}] + self.chat_history[-5:]
        total_tokens = self._estimate_tokens(messages)
        self.token_label.setText(str(total_tokens))
        if total_tokens > 800:
            self.token_label.setStyleSheet("color:#ff4444; font-size:10px; min-width:40px;")
            self.chat_output.append(f"[⚠️ Payload alto: {total_tokens} tokens]\n\n")
        self.progress.setVisible(True)
        self.send_btn.setEnabled(False)
        self._run_ai(messages)

    def _run_ai(self, messages, task_label="Procesando..."):
        self._current_task = task_label
        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        worker = AIWorker(messages)
        worker.finished.connect(self._on_ai_response)
        worker.error.connect(self._on_ai_error)
        worker.start()
        self._worker = worker

    def _on_ai_response(self, text):
        self.progress.setVisible(False)
        self.send_btn.setEnabled(True)
        self.chat_output.append(f"AI:\n{text}\n\n")
        self.chat_history.append({"role": "assistant", "content": text})
        tokens_in = self._estimate_tokens([{"role": "user", "content": self.chat_input.text()}])
        tokens_out = len(text) // 3 + 5
        self._record_tokens(tokens_in, tokens_out)

    def _on_ai_error(self, error):
        self.progress.setVisible(False)
        self.send_btn.setEnabled(True)
        self.chat_output.append(f"[Error: {error}]\n\n")

    # [006] ACCIONES RÁPIDAS EDIT
    def _load_actions(self):
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return list(DEFAULT_ACTIONS)

    def _save_actions(self):
        os.makedirs(os.path.dirname(ACTIONS_FILE), exist_ok=True)
        with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._actions, f, ensure_ascii=False, indent=2)

    def _refresh_actions_list(self):
        self.actions_list.clear()
        for a in self._actions:
            self.actions_list.addItem(a["label"])

    def _add_action(self):
        label, ok = QInputDialog.getText(self, "Nueva accion rapida", "Nombre de la accion:")
        if not ok or not label.strip():
            return
        prompt, ok = QInputDialog.getMultiLineText(
            self, "Prompt de la accion",
            "Prompt que se enviara a la IA (dejar vacio para usar por defecto):"
        )
        if not ok:
            return
        self._actions.append({"label": label.strip(), "prompt": prompt.strip(), "action": "custom"})
        self._save_actions()
        self._refresh_actions_list()

    def _edit_action(self, item):
        idx = self.actions_list.row(item)
        if idx < 0 or idx >= len(self._actions):
            return
        act = self._actions[idx]
        if act.get("action") != "custom":
            QMessageBox.information(self, "Accion fija", "Esta accion es del sistema y no se puede editar.")
            return
        label, ok = QInputDialog.getText(self, "Editar accion", "Nombre:", text=act["label"])
        if ok and label.strip():
            act["label"] = label.strip()
        prompt, ok = QInputDialog.getMultiLineText(self, "Editar prompt", "Prompt:", text=act.get("prompt", ""))
        if ok:
            act["prompt"] = prompt.strip()
        self._save_actions()
        self._refresh_actions_list()

    def _delete_action(self, idx):
        if idx < 0 or idx >= len(self._actions):
            return
        act = self._actions[idx]
        if act.get("action") != "custom":
            QMessageBox.information(self, "Accion fija", "No se puede eliminar una accion del sistema.")
            return
        resp = QMessageBox.question(self, "Eliminar", f"Eliminar '{act['label']}'?")
        if resp == QMessageBox.Yes:
            self._actions.pop(idx)
            self._save_actions()
            self._refresh_actions_list()

    def _action_context_menu(self, pos):
        item = self.actions_list.itemAt(pos)
        if not item:
            return
        idx = self.actions_list.row(item)
        menu = QMenu(self)
        edit_action = menu.addAction("Editar")
        edit_action.triggered.connect(lambda: self._edit_action(item))
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self._delete_action(idx))
        menu.exec(self.actions_list.mapToGlobal(pos))

    def _run_selected_action(self):
        item = self.actions_list.currentItem()
        if not item:
            return
        idx = self.actions_list.row(item)
        act = self._actions[idx]
        action_type = act.get("action", "custom")

        if action_type == "scrape":
            self._scrape_scene()
        elif action_type == "improve_desc":
            self._improve_description()
        elif action_type == "gen_post":
            self._generate_post()
        elif action_type == "analyze":
            self._analyze_code()
        elif action_type == "custom" and act.get("prompt"):
            self._run_custom_action(act["prompt"])
        else:
            self._run_custom_action(item.text())

    # [007] HELPERS
    def _estimate_tokens(self, messages):
        total = 0
        for m in messages:
            c = m.get("content", "")
            total += len(c) // 3 + 5
        return total

    def _update_token_count(self):
        text = self.chat_input.text()
        est = len(text) // 3 + 5
        if est > 400:
            self.token_label.setStyleSheet("color:#ff4444; font-size:10px; min-width:40px;")
        elif est > 250:
            self.token_label.setStyleSheet("color:#cc8800; font-size:10px; min-width:40px;")
        else:
            self.token_label.setStyleSheet("color:#7a6346; font-size:10px; min-width:40px;")
        self.token_label.setText(str(est))

    # [007] TOKEN HISTORY
    def _load_usage(self):
        if os.path.exists(USAGE_FILE):
            try:
                with open(USAGE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_usage(self, entry):
        usage = self._load_usage()
        usage.append(entry)
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)

    def _record_tokens(self, tokens_in, tokens_out):
        now = datetime.now()
        self._save_usage({
            "ts": now.isoformat(),
            "in": tokens_in,
            "out": tokens_out,
        })
        self._refresh_usage_stats()

    def _refresh_usage_stats(self):
        usage = self._load_usage()
        now = datetime.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = day_start - timedelta(days=now.weekday())
        month_start = day_start.replace(day=1)

        total_day = sum(e.get("in", 0) + e.get("out", 0) for e in usage
                        if datetime.fromisoformat(e["ts"]) >= day_start)
        total_week = sum(e.get("in", 0) + e.get("out", 0) for e in usage
                         if datetime.fromisoformat(e["ts"]) >= week_start)
        total_month = sum(e.get("in", 0) + e.get("out", 0) for e in usage
                          if datetime.fromisoformat(e["ts"]) >= month_start)
        total_all = sum(e.get("in", 0) + e.get("out", 0) for e in usage)

        self.usage_day.setText(f"Hoy: {total_day:,} tokens")
        self.usage_week.setText(f"Semana: {total_week:,} tokens")
        self.usage_month.setText(f"Mes: {total_month:,} tokens")
        self.usage_total.setText(f"Total: {total_all:,} tokens")

    # [008] HELPERS
    def _estimate_tokens(self, messages):
        total = 0
        for m in messages:
            c = m.get("content", "")
            total += len(c) // 3 + 5
        return total

    def _update_token_count(self):
        text = self.chat_input.text()
        est = len(text) // 3 + 5
        if est > 400:
            self.token_label.setStyleSheet("color:#ff4444; font-size:10px; min-width:40px;")
        elif est > 250:
            self.token_label.setStyleSheet("color:#cc8800; font-size:10px; min-width:40px;")
        else:
            self.token_label.setStyleSheet("color:#7a6346; font-size:10px; min-width:40px;")
        self.token_label.setText(str(est))

    def get_context_for_tab(self):
        if self.scene_data:
            return scraper.get_scene_summary()
        return ""
