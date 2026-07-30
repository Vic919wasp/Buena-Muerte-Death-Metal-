"""
CONTEXTO: Widget de vista previa del sitio web con QWebEngineView.
           Carga directo el HTML desde DESARROLLO (los datos ya
           están embebidos en el HTML, como videos).
           Toolbar de controles en la parte inferior.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONFIG      - línea 13
[002] PREVIEW WIDGET        - línea 22
[003] LOAD / NAVEGACION     - línea 97
[004] REFRESH               - línea 116
"""
import os
import time
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

# [001] IMPORTS / CONFIG
SITE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "BM WEB"))
DEFAULT_PAGE = "tour.html"

# Desactivar caché HTTP para que recargue JS/CSS desde disco
_profile = QWebEngineProfile.defaultProfile()
_profile.setHttpCacheType(QWebEngineProfile.NoCache)


# [002] PREVIEW WIDGET
class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._page_name = DEFAULT_PAGE
        self._auto_refresh = True
        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._auto_refresh_tick)
        self._timer.start()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.web_view = QWebEngineView()
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.web_view.page().javaScriptConsoleMessage = self._on_js_console
        layout.addWidget(self.web_view)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 2, 4, 2)
        toolbar.setSpacing(4)

        self.refresh_btn = QPushButton("Refrescar preview")
        self.refresh_btn.setFixedHeight(28)
        self.refresh_btn.setStyleSheet(
            "QPushButton{background:#1a1d20;color:#c8ccd0;border:1px solid #1f2225;padding:2px 10px;font-size:11px;}"
            "QPushButton:hover{border-color:#7a6346;}"
        )
        self.refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self.refresh_btn)

        self.auto_btn = QPushButton("Auto: ON")
        self.auto_btn.setFixedHeight(28)
        self.auto_btn.setCheckable(True)
        self.auto_btn.setChecked(True)
        self.auto_btn.setStyleSheet(
            "QPushButton{background:#1a3a1a;color:#c8ccd0;border:1px solid #1f2225;padding:2px 10px;font-size:11px;}"
            "QPushButton:checked{background:#2a5a2a;color:#e8e6df;}"
            "QPushButton:!checked{background:#3a1a1a;color:#c8ccd0;}"
        )
        self.auto_btn.clicked.connect(self._toggle_auto_refresh)
        toolbar.addWidget(self.auto_btn)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color:#7a6346;font-size:11px;")
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self._load()

    def _on_js_console(self, level, msg, line, source):
        source_lower = (source or "").lower()
        if "facebook.com/plugins" in source_lower or "errorutils caught an error" in msg.lower():
            return
        print(f"[Preview JS] [{level}] {msg} (at {source}:{line})")

    def _toggle_auto_refresh(self):
        self._auto_refresh = self.auto_btn.isChecked()
        if self._auto_refresh:
            self._timer.start()
            self.auto_btn.setText("Auto: ON")
            self.auto_btn.setStyleSheet(
                "QPushButton{background:#1a3a1a;color:#c8ccd0;border:1px solid #1f2225;padding:2px 10px;font-size:11px;}"
                "QPushButton:checked{background:#2a5a2a;color:#e8e6df;}"
                "QPushButton:!checked{background:#3a1a1a;color:#c8ccd0;}"
            )
        else:
            self._timer.stop()
            self.auto_btn.setText("Auto: OFF")
            self.auto_btn.setStyleSheet(
                "QPushButton{background:#1a1d20;color:#c8ccd0;border:1px solid #1f2225;padding:2px 10px;font-size:11px;}"
                "QPushButton:hover{border-color:#7a6346;}"
            )

    def _load(self):
        page_path = os.path.join(SITE_ROOT, self._page_name)
        if not os.path.exists(page_path):
            self.status_label.setText(f"Archivo no encontrado: {self._page_name}")
            return
        url = QUrl.fromLocalFile(page_path)
        url.setQuery(f"preview={time.time_ns()}")
        self.web_view.setUrl(url)
        self.status_label.setText(f"Cargando: {self._page_name}")

    def set_page(self, page_name):
        # [003] NAVEGACION / REFRESH
        if page_name == self._page_name:
            self.refresh()
            return
        self._page_name = page_name
        self._load()

    def refresh(self):
        self._load()
        self.status_label.setText(f"Actualizando: {self._page_name}")

    def _auto_refresh_tick(self):
        if self._auto_refresh:
            self.refresh()
