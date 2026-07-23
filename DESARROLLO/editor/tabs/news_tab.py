"""
CONTEXTO: Pestaña de gestión de noticias. CRUD con previsualización
          y edición de artículos del sitio.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 12
[002] UI / TABLA            - línea 25
[003] CRUD                  - línea 80
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView,
)
from PySide6.QtCore import Qt
from services.html_generator import get_news, save_news


# [001] IMPORTS / CLASE
class NewsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_data()

    # [002] UI / TABLA
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Noticias")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        form = QVBoxLayout()
        row1 = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Título del artículo")
        self.thumb_input = QLineEdit()
        self.thumb_input.setPlaceholderText("Ruta imagen (ej: assets/posts/post-01.jpg)")
        row1.addWidget(self.title_input)
        row1.addWidget(self.thumb_input)
        form.addLayout(row1)

        row2 = QHBoxLayout()
        self.date_day_input = QLineEdit()
        self.date_day_input.setPlaceholderText("Día (ej: 02·08)")
        self.date_day_input.setMaximumWidth(120)
        self.date_text_input = QLineEdit()
        self.date_text_input.setPlaceholderText("Texto fecha (ej: 2024)")
        self.date_text_input.setMaximumWidth(120)
        row2.addWidget(self.date_day_input)
        row2.addWidget(self.date_text_input)
        form.addLayout(row2)

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Contenido del artículo (acepta HTML)")
        self.body_input.setMaximumHeight(100)
        form.addWidget(self.body_input)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Agregar artículo")
        self.add_btn.clicked.connect(self._add)
        btn_row.addWidget(self.add_btn)
        form.addLayout(btn_row)
        layout.addLayout(form)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Título", "Fecha", "Imagen", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.clicked.connect(self._on_select)
        layout.addWidget(self.table)

        save_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar cambios")
        self.save_btn.clicked.connect(self._save)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        save_row.addWidget(self.save_btn)
        save_row.addWidget(self.refresh_btn)
        layout.addLayout(save_row)

    # [003] CRUD
    def load_data(self):
        self.articles = get_news()
        self.table.setRowCount(len(self.articles))
        for i, a in enumerate(self.articles):
            self.table.setItem(i, 0, QTableWidgetItem(a.get("title", "")))
            self.table.setItem(i, 1, QTableWidgetItem(a.get("date_day", "") + a.get("date_text", "")))
            self.table.setItem(i, 2, QTableWidgetItem(a.get("thumb", "")))
            del_btn = QPushButton("Eliminar")
            del_btn.clicked.connect(lambda _, row=i: self._delete(row))
            self.table.setCellWidget(i, 3, del_btn)

    def _on_select(self, index):
        row = index.row()
        if row < len(self.articles):
            a = self.articles[row]
            self.title_input.setText(a.get("title", ""))
            self.thumb_input.setText(a.get("thumb", ""))
            self.date_day_input.setText(a.get("date_day", ""))
            self.date_text_input.setText(a.get("date_text", ""))
            self.body_input.setPlainText(a.get("body", ""))

    def _add(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "El título es obligatorio.")
            return
        self.articles.append({
            "title": title,
            "date_day": self.date_day_input.text().strip(),
            "date_text": self.date_text_input.text().strip(),
            "thumb": self.thumb_input.text().strip(),
            "body": self.body_input.toPlainText().strip(),
        })
        save_news(self.articles)
        self._clear_form()
        self.load_data()

    def _delete(self, row):
        confirm = QMessageBox.question(
            self, "Eliminar", f"¿Eliminar '{self.articles[row].get('title', '')}'?",
        )
        if confirm == QMessageBox.Yes:
            self.articles.pop(row)
            save_news(self.articles)
            self.load_data()

    def _save(self):
        save_news(self.articles)
        QMessageBox.information(self, "Guardado", "Noticias guardadas correctamente.")

    def _clear_form(self):
        self.title_input.clear()
        self.thumb_input.clear()
        self.date_day_input.clear()
        self.date_text_input.clear()
        self.body_input.clear()
