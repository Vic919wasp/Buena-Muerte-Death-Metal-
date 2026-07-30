"""
CONTEXTO: Editor de contenido multisite. App PySide6/Qt
            con split-pane: preview del sitio a la izquierda,
            pestañas de edición a la derecha.
            Lee site_config.json para configuración dinámica
            o usa pestañas fijas para Buena Muerte (legacy).
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONFIG      - línea 22
[002] VENTANA PRINCIPAL     - línea 60
[003] MAIN                  - línea ~308
"""
import json
import sys
import os
from datetime import datetime

EDITOR_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE_ROOT = os.path.join(EDITOR_ROOT, "BM WEB")

if not sys.argv or not sys.argv[0]:
    sys.argv = ['main.py']

# Crear QApplication ANTES de cualquier otro import de Qt
# para evitar el warning "Please instantiate the QApplication object first"
from PySide6.QtWidgets import QApplication
_app = QApplication(sys.argv)

# [001] IMPORTS / CONFIG
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QSplitter, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont, QColor, QPalette, QAction

from preview_widget import PreviewWidget
from tabs.tour_tab import TourTab
from tabs.news_tab import NewsTab
from tabs.band_tab import BandTab
from tabs.videos_tab import VideosTab
from tabs.contact_tab import ContactTab
from tabs.newsletter_tab import NewsletterTab
from tabs.settings_tab import SettingsTab
from tabs.content_tab import ContentPipelineTab
from tabs.generic_tab import GenericTab

TAB_PAGES = [
    "tour.html", "news.html", "news.html", "video.html", "band.html",
    "contact.html", "newsletter.html", "index.html", "index.html",
]


# [002] VENTANA PRINCIPAL
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buena Muerte — Editor de Contenido")
        self.setMinimumSize(1200, 700)
        self._preview = None
        self._settings = QSettings("BuenaMuerte", "ContentEditor")
        self._setup_menu()
        self._setup_ui()
        self._restore_state()


    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Sitio")

        new_site_action = QAction("Nuevo sitio...", self)
        new_site_action.triggered.connect(self._new_site)
        file_menu.addAction(new_site_action)

        open_site_action = QAction("Seleccionar carpeta...", self)
        open_site_action.triggered.connect(self._open_site)
        file_menu.addAction(open_site_action)

        new_page_action = QAction("Nueva página...", self)
        new_page_action.triggered.connect(self._new_page)
        file_menu.addAction(new_page_action)

        file_menu.addSeparator()
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _new_site(self):
        import subprocess
        script = os.path.join(EDITOR_ROOT, "nueva_web.py")
        if os.path.exists(script):
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                subprocess.Popen([sys.executable, script], cwd=os.path.dirname(os.path.abspath(__file__)), startupinfo=si)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo lanzar el asistente: {e}")
        else:
            QMessageBox.warning(self, "Nuevo sitio", "No se encontro nueva_web.py en el directorio del editor.")

    def _open_site(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta del sitio")
        if folder:
            config_path = os.path.join(folder, "site_config.json")
            if os.path.exists(config_path):
                QMessageBox.information(
                    self, "Sitio seleccionado",
                    f"Sitio seleccionado: {folder}\nEdita site_config.json y reinicia el editor para aplicar."
                )
            else:
                QMessageBox.warning(
                    self, "Sin config",
                    "No se encontro site_config.json en esta carpeta. Use Nuevo sitio para crearlo."
                )

    def _new_page(self):
        from PySide6.QtWidgets import QInputDialog, QComboBox
        name, ok = QInputDialog.getText(self, "Nueva página", "Nombre del archivo (ej: about.html):")
        if not ok or not name.strip():
            return
        name = name.strip()
        if not name.endswith(".html"):
            name += ".html"

        types = ["content", "contact", "news", "photo"]
        tab_type, ok2 = QInputDialog.getItem(
            self, "Tipo de página", "Tipo de tab:", types, 0, False
        )
        if not ok2:
            return

        fields_map = {
            "content": ["title", "body"],
            "contact": ["email", "phone", "address"],
            "news": ["title", "date", "body", "thumb"],
            "photo": ["title", "image"],
        }
        fields = fields_map.get(tab_type, ["title", "body"])

        config_path = os.path.join(EDITOR_ROOT, "site_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {"site_name": "Nuevo Sitio", "site_title": "Nuevo Sitio", "pages": []}

        config["pages"].append({
            "file": name,
            "label": name.replace(".html", "").replace("_", " ").title(),
            "tab_type": tab_type,
            "fields": fields,
        })
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        QMessageBox.information(
            self, "Página creada",
            f"Página {name} agregada.\nSeleccion\u00e1 Sitio > Seleccionar carpeta para recargar."
        )

    def _load_site_config(self):
        config_path = os.path.join(EDITOR_ROOT, "site_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Buena Muerte — Editor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-family:'Cinzel',serif; font-size:22px; color:#c8ccd0; "
            "padding:12px; background:#0a0c0d; border-bottom:1px solid #1f2225;"
        )
        main_layout.addWidget(title)

        splitter = QSplitter(Qt.Horizontal)
        self._splitter = splitter
        splitter.setHandleWidth(6)
        splitter.setChildrenCollapsible(True)

        self._preview = PreviewWidget()
        splitter.addWidget(self._preview)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        config = self._load_site_config()

        if config:
            self._tab_pages = config.get("pages", [])
            for p in self._tab_pages:
                tabs.addTab(GenericTab(p, self._refresh_preview), p.get("label", p["file"]))
            self._TAB_PAGES = [p["file"] for p in self._tab_pages]
        else:
            self._tab_pages = None
            tabs.addTab(TourTab(self._refresh_preview), "Fechas")
            tabs.addTab(NewsTab(self._refresh_preview), "Noticias")
            tabs.addTab(ContentPipelineTab(self._refresh_preview), "Pipeline")
            tabs.addTab(VideosTab(self._refresh_preview), "Videos")
            tabs.addTab(BandTab(self._refresh_preview), "Banda")
            tabs.addTab(ContactTab(self._refresh_preview), "Contacto")
            tabs.addTab(NewsletterTab(self._refresh_preview), "Newsletter")
            tabs.addTab(SettingsTab(self._refresh_preview), "Publicar")
            self._TAB_PAGES = TAB_PAGES

        tabs.currentChanged.connect(self._show_tab_page)
        self._tabs = tabs
        from PySide6.QtGui import QShortcut, QKeySequence

        for i in range(min(9, tabs.count())):
            sc = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            sc.activated.connect(lambda idx=i: tabs.setCurrentIndex(idx))

        right_layout.addWidget(tabs)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([200, 1000])
        main_layout.addWidget(splitter)
        self._show_tab_page(0)

    def _refresh_preview(self):
        if self._preview:
            self._preview.refresh()

    def _show_tab_page(self, index):
        pages = getattr(self, "_TAB_PAGES", TAB_PAGES)
        if self._preview and 0 <= index < len(pages):
            self._preview.set_page(pages[index])

    def closeEvent(self, event):
        if hasattr(self, "_splitter"):
            self._settings.setValue("splitter_sizes", self._splitter.sizes())
        if hasattr(self, "_tabs"):
            self._settings.setValue("current_tab", self._tabs.currentIndex())
        super().closeEvent(event)

    def _restore_state(self):
        sizes = self._settings.value("splitter_sizes")
        if sizes:
            try:
                sizes = [int(s) for s in sizes]
                self._splitter.setSizes(sizes)
            except Exception:
                pass

        idx = self._settings.value("current_tab")
        if idx is not None:
            try:
                self._tabs.setCurrentIndex(int(idx))
                self._show_tab_page(int(idx))
            except Exception:
                pass

# [003] MAIN
def _load_themes():
    themes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes.json")
    if os.path.exists(themes_path):
        with open(themes_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"active": "dark_amber", "themes": {"dark_amber": {}}}


def setup_theme(app, theme_name=None):
    themes_data = _load_themes()
    if not theme_name:
        theme_name = themes_data.get("active", "dark_amber")
    themes = themes_data.get("themes", {})
    theme = themes.get(theme_name)
    if not theme and themes:
        theme = themes.get(list(themes.keys())[0], {})

    app.setStyle("Fusion")
    if theme:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(theme["window"]))
        palette.setColor(QPalette.WindowText, QColor(theme["window_text"]))
        palette.setColor(QPalette.Base, QColor(theme["base"]))
        palette.setColor(QPalette.AlternateBase, QColor(theme["alternate_base"]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme["tool_tip_base"]))
        palette.setColor(QPalette.ToolTipText, QColor(theme["tool_tip_text"]))
        palette.setColor(QPalette.Text, QColor(theme["text"]))
        palette.setColor(QPalette.Button, QColor(theme["button"]))
        palette.setColor(QPalette.ButtonText, QColor(theme["button_text"]))
        palette.setColor(QPalette.Highlight, QColor(theme["highlight"]))
        palette.setColor(QPalette.HighlightedText, QColor(theme["highlighted_text"]))
        app.setPalette(palette)
    font = app.font()
    font.setPointSize(11)
    app.setFont(font)

    styles = theme.get("styles", {}) if theme else {}
    style_str = "\n".join("{} {{ {} }}".format(k, v) for k, v in styles.items())
    app.setStyleSheet(style_str)


if __name__ == "__main__":
    import traceback
    log_path = os.path.join(os.path.dirname(__file__), "error.log")
    try:
        setup_theme(_app)
        window = MainWindow()
        window.show()
        sys.exit(_app.exec())
    except Exception:
        tb = traceback.format_exc()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n{datetime.now().isoformat()}\n{tb}\n")
        print(tb)
        raise
