"""
CONTEXTO: Editor de contenido del sitio Buena Muerte. App PySide6/Qt
          que permite gestionar tour, noticias, banda, newsletter y
          publicar cambios al sitio desplegado en Render.com.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONFIG      - línea 12
[002] VENTANA PRINCIPAL     - línea 25
[003] MAIN                  - línea 50
"""
import sys
import os

# [001] IMPORTS / CONFIG
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

from tabs.tour_tab import TourTab
from tabs.news_tab import NewsTab
from tabs.band_tab import BandTab
from tabs.videos_tab import VideosTab
from tabs.contact_tab import ContactTab
from tabs.newsletter_tab import NewsletterTab
from tabs.settings_tab import SettingsTab
from tabs.ai_tab import AITab


# [002] VENTANA PRINCIPAL
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Buena Muerte — Editor de Contenido")
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Buena Muerte — Editor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-family:'Cinzel',serif; font-size:22px; color:#c8ccd0; "
            "padding:12px; background:#0a0c0d; border-bottom:1px solid #1f2225;"
        )
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(TourTab(), "Fechas")
        tabs.addTab(NewsTab(), "Noticias")
        tabs.addTab(VideosTab(), "Videos")
        tabs.addTab(BandTab(), "Banda")
        tabs.addTab(ContactTab(), "Contacto")
        tabs.addTab(NewsletterTab(), "Newsletter")
        tabs.addTab(AITab(), "AI")
        tabs.addTab(SettingsTab(), "Publicar")
        layout.addWidget(tabs)


# [003] MAIN
def setup_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0a0c0d"))
    palette.setColor(QPalette.WindowText, QColor("#c8ccd0"))
    palette.setColor(QPalette.Base, QColor("#111416"))
    palette.setColor(QPalette.AlternateBase, QColor("#1a1d20"))
    palette.setColor(QPalette.ToolTipBase, QColor("#1a1d20"))
    palette.setColor(QPalette.ToolTipText, QColor("#c8ccd0"))
    palette.setColor(QPalette.Text, QColor("#c8ccd0"))
    palette.setColor(QPalette.Button, QColor("#111416"))
    palette.setColor(QPalette.ButtonText, QColor("#c8ccd0"))
    palette.setColor(QPalette.Highlight, QColor("#4a0f0d"))
    palette.setColor(QPalette.HighlightedText, QColor("#e8e6df"))
    app.setPalette(palette)

    app.setStyleSheet("""
        QTabWidget::pane { border: 1px solid #1f2225; }
        QTabBar::tab {
            background: #111416; color: #9aa0a6; padding: 8px 16px;
            border: 1px solid #1f2225; border-bottom: none;
            font-family: 'Cinzel', serif;
        }
        QTabBar::tab:selected { background: #1a1d20; color: #c8ccd0; }
        QTabBar::tab:hover { background: #1f2225; }
        QLineEdit, QTextEdit, QDateEdit {
            background: #111416; color: #c8ccd0; border: 1px solid #1f2225;
            padding: 6px; font-family: 'Inter', sans-serif;
        }
        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus { border-color: #7a6346; }
        QPushButton {
            background: #111416; color: #c8ccd0; border: 1px solid #1f2225;
            padding: 6px 14px; font-family: 'Cinzel', serif;
        }
        QPushButton:hover { border-color: #7a6346; color: #e8e6df; }
        QPushButton:pressed { background: #1a1d20; }
        QTableWidget {
            background: #111416; color: #c8ccd0; gridline-color: #1f2225;
            border: 1px solid #1f2225;
        }
        QTableWidget::item:selected { background: #1a1d20; }
        QHeaderView::section {
            background: #0a0c0d; color: #7a6346; padding: 6px;
            border: 1px solid #1f2225; font-family: 'Cinzel', serif;
        }
        QScrollBar:vertical { background: #111416; width: 8px; }
        QScrollBar::handle:vertical { background: #1f2225; min-height: 20px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
