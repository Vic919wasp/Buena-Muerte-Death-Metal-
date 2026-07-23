"""
CONTEXTO: Pestaña de edición de contacto. Permite modificar email,
          redes sociales y texto de la página de contacto.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 12
[002] UI                    - línea 25
[003] CARGA / GUARDADO      - línea 70
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox,
)
from PySide6.QtCore import Qt
from services.html_generator import _read, _write
import re


class ContactTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Contacto y Redes")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        form = QVBoxLayout()
        form.setSpacing(8)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email de contacto")
        form.addWidget(QLabel("Email:"))
        form.addWidget(self.email_input)

        self.ig_input = QLineEdit()
        self.ig_input.setPlaceholderText("URL Instagram")
        form.addWidget(QLabel("Instagram:"))
        form.addWidget(self.ig_input)

        self.fb_input = QLineEdit()
        self.fb_input.setPlaceholderText("URL Facebook")
        form.addWidget(QLabel("Facebook:"))
        form.addWidget(self.fb_input)

        self.spotify_input = QLineEdit()
        self.spotify_input.setPlaceholderText("URL Spotify Artista")
        form.addWidget(QLabel("Spotify:"))
        form.addWidget(self.spotify_input)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar cambios")
        self.save_btn.clicked.connect(self._save)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

    def load_data(self):
        html = _read("contact.html")
        email_m = re.search(r'mailto:([^"?]+)', html)
        ig_m = re.search(r'href="(https://instagram\.com/[^"]+)"', html)
        fb_m = re.search(r'href="(https://facebook\.com/[^"]+)"', html)
        sp_m = re.search(r'href="(https://open\.spotify\.com/[^"]+)"', html)
        self.email_input.setText(email_m.group(1) if email_m else "")
        self.ig_input.setText(ig_m.group(1) if ig_m else "")
        self.fb_input.setText(fb_m.group(1) if fb_m else "")
        self.spotify_input.setText(sp_m.group(1) if sp_m else "")

    def _save(self):
        email = self.email_input.text().strip()
        ig = self.ig_input.text().strip()
        fb = self.fb_input.text().strip()
        sp = self.spotify_input.text().strip()

        # Update contact.html
        html = _read("contact.html")
        html = re.sub(r'mailto:[^"?]+', f'mailto:{email}', html)
        html = re.sub(r'href="https://instagram\.com/[^"]+"', f'href="{ig}"', html)
        html = re.sub(r'href="https://facebook\.com/[^"]+"', f'href="{fb}"', html)
        html = re.sub(r'href="https://open\.spotify\.com/[^"]+"', f'href="{sp}"', html)
        html = re.sub(r'favioleguizamon2@gmail\.com', email, html)
        _write("contact.html", html)

        # Update footer in all HTML files (email appears there)
        for fname in ["index.html", "news.html", "tour.html", "video.html",
                       "discography.html", "band.html", "newsletter.html"]:
            content = _read(fname)
            if content and email in content:
                continue  # already updated
            if content:
                content = re.sub(r'mailto:[^"?]+', f'mailto:{email}', content)
                content = re.sub(r'favioleguizamon2@gmail\.com', email, content)
                _write(fname, content)

        QMessageBox.information(self, "Guardado", "Contacto y redes guardados.")
