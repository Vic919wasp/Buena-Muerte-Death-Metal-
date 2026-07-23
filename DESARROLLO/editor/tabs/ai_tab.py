"""
CONTEXTO: Pestaña de asistente AI para el editor. Integra Ollama para
          mejorar textos, generar posts, analizar la escena metal ARG
          y asistir en la gestión del sitio.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 14
[002] UI / LAYOUT           - línea 35
[003] ACCIONES AI           - línea 100
[004] CHAT                  - línea 150
[005] HELPERS               - línea 200
"""
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QFrame, QSplitter, QMessageBox,
    QComboBox, QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal

from services import ai_service
from services import scraper
from services.prompt_builder import (
    build_improve_description_prompt,
    build_improve_existing_prompt,
    build_generate_post_prompt,
    build_quick_prompt,
)


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


# [002] UI / LAYOUT
class AITab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_data = None
        self.chat_history = []
        self._worker = None
        self._setup_ui()
        self._check_ollama()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QLabel("Asistente AI")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        self.status_label = QLabel("Verificando Ollama...")
        self.status_label.setStyleSheet("color:#9aa0a6; font-size:11px;")
        layout.addWidget(self.status_label)

        actions_frame = QFrame()
        actions_frame.setStyleSheet("QFrame{border:1px solid #1f2225; padding:8px;}")
        actions_l = QVBoxLayout(actions_frame)

        actions_header = QLabel("Acciones rapidas")
        actions_header.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif;")
        actions_l.addWidget(actions_header)

        btn_row1 = QHBoxLayout()
        self.scrape_btn = QPushButton("Actualizar escena ARG")
        self.scrape_btn.clicked.connect(self._scrape_scene)
        btn_row1.addWidget(self.scrape_btn)
        self.improve_desc_btn = QPushButton("Mejorar descripcion seleccionada")
        self.improve_desc_btn.clicked.connect(self._improve_description)
        btn_row1.addWidget(self.improve_desc_btn)
        actions_l.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        self.gen_post_btn = QPushButton("Generar post para redes")
        self.gen_post_btn.clicked.connect(self._generate_post)
        btn_row2.addWidget(self.gen_post_btn)
        self.analyze_btn = QPushButton("Analizar codigo del sitio")
        self.analyze_btn.clicked.connect(self._analyze_code)
        btn_row2.addWidget(self.analyze_btn)
        actions_l.addLayout(btn_row2)

        layout.addWidget(actions_frame)

        scene_frame = QFrame()
        scene_frame.setStyleSheet("QFrame{border:1px solid #1f2225; padding:8px;}")
        scene_l = QVBoxLayout(scene_frame)
        scene_header = QLabel("Escena metal Argentina")
        scene_header.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif;")
        scene_l.addWidget(scene_header)
        self.scene_text = QTextEdit()
        self.scene_text.setReadOnly(True)
        self.scene_text.setMaximumHeight(120)
        self.scene_text.setPlaceholderText("Haz clic en 'Actualizar escena ARG' para cargar shows y noticias...")
        scene_l.addWidget(self.scene_text)
        layout.addWidget(scene_frame)

        layout.addWidget(QLabel("Chat con AI:"))
        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setStyleSheet("QTextEdit{font-family:'Inter',sans-serif;}")
        layout.addWidget(self.chat_output)

        chat_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribi tu pregunta o pedilo...")
        self.chat_input.returnPressed.connect(self._send_chat)
        self.chat_input.textChanged.connect(self._update_token_count)
        chat_row.addWidget(self.chat_input)
        self.token_label = QLabel("0 tokens")
        self.token_label.setStyleSheet("color:#7a6346; font-size:10px; min-width:60px;")
        chat_row.addWidget(self.token_label)
        self.send_btn = QPushButton("Enviar")
        self.send_btn.clicked.connect(self._send_chat)
        chat_row.addWidget(self.send_btn)
        layout.addLayout(chat_row)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar{border:1px solid #1f2225; height:4px;} QProgressBar::chunk{background:#4a0f0d;}")
        layout.addWidget(self.progress)

    # [003] ACCIONES AI
    def _check_ollama(self):
        if ai_service.OllamaClient().is_available():
            self.status_label.setText("Ollama conectado (llama3.2:3b)")
            self.status_label.setStyleSheet("color:#4a9; font-size:11px;")
        else:
            self.status_label.setText("Ollama no detectado. Inicia Ollama para usar el asistente.")
            self.status_label.setStyleSheet("color:#a44; font-size:11px;")

    def _scrape_scene(self):
        self.scrape_btn.setEnabled(False)
        self.scrape_btn.setText("Scrapeando...")
        self.progress.setVisible(True)

        class ScraperWorker(QThread):
            finished = Signal(dict)
            def run(self):
                try:
                    data = scraper.force_refresh()
                    self.finished.emit(data)
                except Exception:
                    self.finished.emit({"error": "Error al scrapeart"})

        worker = ScraperWorker()
        worker.finished.connect(self._on_scene_loaded)
        worker.start()
        self._scraper_worker = worker

    def _on_scene_loaded(self, data):
        self.progress.setVisible(False)
        self.scrape_btn.setEnabled(True)
        self.scrape_btn.setText("Actualizar escena ARG")
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
            "lugar": "EL TEATRITO",
            "ciudad": "CABA",
            "dia": "27",
            "mes": "OCT",
            "anio": "2026",
            "descripcion": "Show de Buena Muerte en El Teatrito",
        }
        self.progress.setVisible(True)
        self.improve_desc_btn.setEnabled(False)
        messages = build_improve_description_prompt(event, self.scene_data)
        self._run_ai(messages, "Mejorando descripcion...")

    def _generate_post(self):
        if not self.scene_data:
            QMessageBox.information(self, "Escena", "Primero actualiza la escena ARG.")
            return
        event = {
            "lugar": "EL TEATRITO",
            "ciudad": "CABA",
            "dia": "27",
            "mes": "OCT",
            "anio": "2026",
            "descripcion": "Buena Muerte + Six Feet Under",
        }
        self.progress.setVisible(True)
        self.gen_post_btn.setEnabled(False)
        messages = build_generate_post_prompt(event, self.scene_data)
        self._run_ai(messages, "Generando post...")

    def _analyze_code(self):
        self.progress.setVisible(True)
        self.analyze_btn.setEnabled(False)
        from services import html_generator
        code = html_generator._read("assets/js.js")[:3000]
        messages = [
            {"role": "system", "content": "Sos un experto en Python/JS/PySide6. Analiza el codigo y sugiere mejoras. Responde en español."},
            {"role": "user", "content": f"Analiza este codigo del sitio web de una banda de metal:\n\n```\n{code}\n```"},
        ]
        self._run_ai(messages, "Analizando codigo...")

    # [004] CHAT
    def _send_chat(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        text = text[:500]
        self.chat_input.clear()
        self.chat_output.append(f"Tu: {text}\n")
        self.chat_history.append({"role": "user", "content": text})
        ctx = (scraper.get_scene_summary() if self.scene_data else "")[:500]
        system_msg = {
            "role": "system",
            "content": (
                "Sos el asistente de Buena Muerte, banda de death metal de "
                "Zona Sur, AMBA, Argentina. Respondé en español, sé conciso y útil. "
                f"Contexto de escena ARG:\n{ctx}" if ctx else
                "Sos el asistente de Buena Muerte, banda de death metal de "
                "Zona Sur, AMBA, Argentina. Respondé en español, sé conciso y útil."
            ),
        }
        messages = [system_msg] + self.chat_history[-5:]
        total_tokens = self._estimate_tokens(messages)
        self.token_label.setText(f"{total_tokens} tokens")
        if total_tokens > 800:
            self.token_label.setStyleSheet("color:#ff4444; font-size:10px; min-width:60px;")
            self.chat_output.append(f"[⚠️ Payload alto: {total_tokens} tokens — respuesta puede tardar]\n\n")
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
        self.improve_desc_btn.setEnabled(True)
        self.gen_post_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.chat_output.append(f"AI:\n{text}\n\n")
        self.chat_history.append({"role": "assistant", "content": text})

    def _on_ai_error(self, error):
        self.progress.setVisible(False)
        self.send_btn.setEnabled(True)
        self.improve_desc_btn.setEnabled(True)
        self.gen_post_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.chat_output.append(f"[Error: {error}]\n\n")

    # [005] HELPERS
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
            self.token_label.setStyleSheet("color:#ff4444; font-size:10px; min-width:60px;")
        elif est > 250:
            self.token_label.setStyleSheet("color:#cc8800; font-size:10px; min-width:60px;")
        else:
            self.token_label.setStyleSheet("color:#7a6346; font-size:10px; min-width:60px;")
        self.token_label.setText(f"{est} tokens")

    def get_context_for_tab(self):
        """Retorna contexto de escena para usar en otros tabs."""
        if self.scene_data:
            return scraper.get_scene_summary()
        return ""
