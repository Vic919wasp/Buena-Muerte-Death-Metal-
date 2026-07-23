"""
CONTEXTO: Pestaña de edición de información de la banda. Bio, miembros
          (nombre, instrumento, foto) y galería de imágenes.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 14
[002] UI                    - línea 28
[003] CARGA / GUARDADO      - línea 100
"""
import os
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QFrame,
)
from PySide6.QtCore import Qt
from services.html_generator import (
    get_bio, get_members, _read, _write, SITE_ROOT
)
import re

GALLERY_DIR = os.path.join(SITE_ROOT, "assets", "posts")


class BandTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        os.makedirs(GALLERY_DIR, exist_ok=True)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QLabel("Información de la Banda")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        bio_label = QLabel("Biografía:")
        bio_label.setStyleSheet("color:#9aa0a6; font-size:11px;")
        layout.addWidget(bio_label)
        self.bio_edit = QTextEdit()
        self.bio_edit.setPlaceholderText("Biografía de la banda...")
        self.bio_edit.setMaximumHeight(100)
        layout.addWidget(self.bio_edit)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color:#1f2225;")
        layout.addWidget(sep1)

        members_label = QLabel("Miembros de la banda:")
        members_label.setStyleSheet("color:#9aa0a6; font-size:11px;")
        layout.addWidget(members_label)

        mform = QHBoxLayout()
        self.m_name = QLineEdit()
        self.m_name.setPlaceholderText("Nombre *")
        self.m_role = QLineEdit()
        self.m_role.setPlaceholderText("Instrumento")
        self.m_photo = QLineEdit()
        self.m_photo.setPlaceholderText("Ruta foto (ej: assets/member-favio.jpg)")
        self.m_photo_btn = QPushButton("Examinar")
        self.m_photo_btn.clicked.connect(self._pick_member_photo)
        mform.addWidget(self.m_name)
        mform.addWidget(self.m_role)
        mform.addWidget(self.m_photo)
        mform.addWidget(self.m_photo_btn)
        self.add_member_btn = QPushButton("+ Agregar miembro")
        self.add_member_btn.clicked.connect(self._add_member)
        mform.addWidget(self.add_member_btn)
        layout.addLayout(mform)

        self.members_table = QTableWidget()
        self.members_table.setColumnCount(4)
        self.members_table.setHorizontalHeaderLabels(["Nombre", "Instrumento", "Foto", "Acción"])
        self.members_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.members_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.members_table.setMaximumHeight(150)
        layout.addWidget(self.members_table)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color:#1f2225;")
        layout.addWidget(sep2)

        gal_label = QLabel("Galería de imágenes:")
        gal_label.setStyleSheet("color:#9aa0a6; font-size:11px;")
        layout.addWidget(gal_label)

        gal_row = QHBoxLayout()
        self.add_gal_btn = QPushButton("+ Agregar fotos a galería")
        self.add_gal_btn.clicked.connect(self._add_gallery)
        self.gal_count_label = QLabel("0 imágenes")
        self.gal_count_label.setStyleSheet("color:#7a6346; font-size:11px;")
        gal_row.addWidget(self.add_gal_btn)
        gal_row.addWidget(self.gal_count_label)
        gal_row.addStretch()
        layout.addLayout(gal_row)

        self.gal_table = QTableWidget()
        self.gal_table.setColumnCount(3)
        self.gal_table.setHorizontalHeaderLabels(["Archivo", "Ruta", "Acción"])
        self.gal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.gal_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.gal_table)

        btn_row = QHBoxLayout()
        self.save_bio_btn = QPushButton("Guardar biografía")
        self.save_bio_btn.clicked.connect(self._save_bio)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_row.addWidget(self.save_bio_btn)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)

    def load_data(self):
        self.bio_text = get_bio()
        self.bio_edit.setPlainText(self.bio_text)
        self.members = get_members()
        self.members_table.setRowCount(len(self.members))
        for i, m in enumerate(self.members):
            self.members_table.setItem(i, 0, QTableWidgetItem(m.get("name", "")))
            self.members_table.setItem(i, 1, QTableWidgetItem(m.get("role", "")))
            self.members_table.setItem(i, 2, QTableWidgetItem(m.get("photo", "")))
            del_btn = QPushButton("Quitar")
            del_btn.clicked.connect(lambda _, row=i: self._del_member(row))
            self.members_table.setCellWidget(i, 3, del_btn)

        # Gallery
        html = _read("band.html")
        self.gallery = re.findall(r'href="(assets/posts/[^"]+)"', html)
        self.gal_table.setRowCount(len(self.gallery))
        self.gal_count_label.setText(f"{len(self.gallery)} imágenes")
        for i, path in enumerate(self.gallery):
            fname = os.path.basename(path)
            self.gal_table.setItem(i, 0, QTableWidgetItem(fname))
            self.gal_table.setItem(i, 1, QTableWidgetItem(path))
            del_btn = QPushButton("Quitar")
            del_btn.clicked.connect(lambda _, row=i: self._del_gallery(row))
            self.gal_table.setCellWidget(i, 2, del_btn)

    def _pick_member_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Foto del miembro", "",
            "Imágenes (*.jpg *.jpeg *.png *.webp);;Todos (*)"
        )
        if path:
            fname = os.path.basename(path)
            dst = os.path.join(SITE_ROOT, "assets", fname)
            shutil.copy2(path, dst)
            self.m_photo.setText("assets/" + fname)

    def _add_member(self):
        name = self.m_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        self.members.append({
            "name": name,
            "role": self.m_role.text().strip(),
            "photo": self.m_photo.text().strip(),
        })
        self._save_members_html()
        self.m_name.clear()
        self.m_role.clear()
        self.m_photo.clear()
        self.load_data()

    def _del_member(self, row):
        confirm = QMessageBox.question(
            self, "Eliminar", f"¿Quitar a {self.members[row].get('name', '')}?",
        )
        if confirm == QMessageBox.Yes:
            self.members.pop(row)
            self._save_members_html()
            self.load_data()

    def _save_members_html(self):
        html = _read("band.html")
        members_html = ""
        for m in self.members:
            members_html += (
                f'\n      <div class="member">\n'
                f'        <div class="member__photo"><img src="{m.get("photo", "")}" alt="{m.get("name", "")}"></div>\n'
                f'        <h3 class="member__name">{m.get("name", "")}</h3>\n'
                f'        <p class="member__role">{m.get("role", "")}</p>\n'
                f'      </div>'
            )
        new_html = re.sub(
            r'(<div class="members">).*?(    </div>\n  </div>\n</section>\n\n<!-- GALER)',
            f"\\1{members_html}\n\\2",
            html,
            flags=re.DOTALL,
        )
        _write("band.html", new_html)

    def _add_gallery(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Agregar fotos a galería", "",
            "Imágenes (*.jpg *.jpeg *.png *.webp);;Todos (*)"
        )
        if not files:
            return
        html = _read("band.html")
        for src in files:
            fname = os.path.basename(src)
            dst = os.path.join(GALLERY_DIR, fname)
            if os.path.exists(dst):
                base, ext = os.path.splitext(fname)
                i = 1
                while os.path.exists(os.path.join(GALLERY_DIR, f"{base}_{i}{ext}")):
                    i += 1
                dst = os.path.join(GALLERY_DIR, f"{base}_{i}{ext}")
                fname = f"{base}_{i}{ext}"
            shutil.copy2(src, dst)
            rel = "assets/posts/" + fname
            new_item = (
                f'      <a class="gallery__item" href="{rel}" target="_blank">'
                f'<img loading="lazy" src="{rel}" alt=""></a>'
            )
            html = html.replace(
                '    </div>\n  </div>\n</section>\n\n<!-- [005]',
                f'{new_item}\n    </div>\n  </div>\n</section>\n\n<!-- [005]'
            )
        _write("band.html", html)
        self.load_data()

    def _del_gallery(self, row):
        confirm = QMessageBox.question(
            self, "Eliminar", f"¿Quitar {os.path.basename(self.gallery[row])}?",
        )
        if confirm == QMessageBox.Yes:
            html = _read("band.html")
            item_path = self.gallery[row]
            html = re.sub(
                rf'\s*<a class="gallery__item" href="{re.escape(item_path)}"[^>]*>.*?</a>',
                "", html
            )
            _write("band.html", html)
            self.load_data()

    def _save_bio(self):
        new_bio = self.bio_edit.toPlainText().strip()
        html = _read("band.html")
        paragraphs = [f"        <p>{p.strip()}</p>" for p in new_bio.split("\n") if p.strip()]
        new_bio_block = "\n".join(paragraphs)
        new_html = re.sub(
            r'(<div class="bio">).*?(</div>)',
            f"\\1\n{new_bio_block}\n      \\2",
            html,
            flags=re.DOTALL,
        )
        _write("band.html", new_html)
        QMessageBox.information(self, "Guardado", "Biografía guardada correctamente.")
