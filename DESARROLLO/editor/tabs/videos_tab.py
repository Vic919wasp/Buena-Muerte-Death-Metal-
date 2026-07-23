"""
CONTEXTO: Gestión de videos de YouTube. CRUD con ID, título y categoría.
          Lee y escribe video.html.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 12
[002] UI / TABLA            - línea 25
[003] CRUD                  - línea 80
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QHeaderView, QComboBox,
)
from PySide6.QtCore import Qt
from services.html_generator import get_videos, save_videos


class VideosTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Videos de YouTube")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        form = QHBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID del video YouTube (ej: naEAB9Jbh8A)")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Título del video")
        self.cat_input = QComboBox()
        self.cat_input.setEditable(True)
        self.cat_input.addItems(["Catalepsia", "En Vivo", "Dios Es Sadico"])
        self.cat_input.setMaximumWidth(180)
        form.addWidget(self.id_input)
        form.addWidget(self.title_input)
        form.addWidget(QLabel("Categoría:"))
        form.addWidget(self.cat_input)
        self.add_btn = QPushButton("Agregar")
        self.add_btn.clicked.connect(self._add)
        form.addWidget(self.add_btn)
        layout.addLayout(form)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["YouTube ID", "Título", "Categoría", "Miniatura", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar cambios")
        self.save_btn.clicked.connect(self._save)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)

    def load_data(self):
        self.videos = get_videos()
        self.table.setRowCount(len(self.videos))
        for i, v in enumerate(self.videos):
            self.table.setItem(i, 0, QTableWidgetItem(v.get("id", "")))
            self.table.setItem(i, 1, QTableWidgetItem(v.get("title", "")))
            self.table.setItem(i, 2, QTableWidgetItem(v.get("category", "")))
            thumb = f"https://img.youtube.com/vi/{v.get('id','')}/hqdefault.jpg"
            self.table.setItem(i, 3, QTableWidgetItem(thumb))
            del_btn = QPushButton("Eliminar")
            del_btn.clicked.connect(lambda _, row=i: self._delete(row))
            self.table.setCellWidget(i, 4, del_btn)

    def _add(self):
        vid = self.id_input.text().strip()
        title = self.title_input.text().strip()
        cat = self.cat_input.currentText().strip()
        if not vid:
            QMessageBox.warning(self, "Error", "El ID del video es obligatorio.")
            return
        self.videos.append({"id": vid, "title": title or vid, "category": cat})
        save_videos(self.videos)
        self.id_input.clear()
        self.title_input.clear()
        self.load_data()

    def _delete(self, row):
        confirm = QMessageBox.question(
            self, "Eliminar", f"¿Eliminar '{self.videos[row].get('title', '')}'?",
        )
        if confirm == QMessageBox.Yes:
            self.videos.pop(row)
            save_videos(self.videos)
            self.load_data()

    def _save(self):
        save_videos(self.videos)
        QMessageBox.information(self, "Guardado", "Videos guardados correctamente.")
