"""
CONTEXTO: Pestaña de visualización y exportación de suscriptores del
          newsletter. Conecta con el backend Flask vía API.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 12
[002] UI / TABLA            - línea 25
[003] ACCIONES              - línea 60
"""
import csv
import io
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView,
)
from PySide6.QtCore import Qt
from services import api_client


# [001] IMPORTS / CLASE
class NewsletterTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subscribers = []
        self._setup_ui()
        self.load_data()

    # [002] UI / TABLA
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Newsletter — Suscriptores")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        self.status_label = QLabel("Conectando con el backend...")
        self.status_label.setStyleSheet("color:#7a6346;")
        layout.addWidget(self.status_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "Email", "Fecha", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        self.export_csv_btn = QPushButton("Exportar CSV")
        self.export_csv_btn.clicked.connect(self._export_csv)
        self.export_json_btn = QPushButton("Exportar JSON")
        self.export_json_btn.clicked.connect(self._export_json)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.export_csv_btn)
        btn_row.addWidget(self.export_json_btn)
        layout.addLayout(btn_row)

    # [003] ACCIONES
    def load_data(self):
        self.status_label.setText("Cargando suscriptores...")
        result = api_client.list_subscribers()
        if result is None:
            self.status_label.setText("No se pudo conectar al backend (¿está corriendo en :5000?)")
            self.subscribers = []
        else:
            self.subscribers = result
            self.status_label.setText(f"{len(self.subscribers)} suscriptores")
        self._fill_table()

    def _fill_table(self):
        self.table.setRowCount(len(self.subscribers))
        for i, s in enumerate(self.subscribers):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(s.get("email", "")))
            self.table.setItem(i, 2, QTableWidgetItem(s.get("subscribed_at", "")))
            del_btn = QPushButton("Eliminar")
            del_btn.clicked.connect(lambda _, sid=s.get("id"): self._delete(sid))
            self.table.setCellWidget(i, 3, del_btn)

    def _delete(self, sid):
        confirm = QMessageBox.question(self, "Eliminar", "¿Eliminar este suscriptor?")
        if confirm == QMessageBox.Yes:
            api_client.delete_subscriber(sid)
            self.load_data()

    def _export_csv(self):
        if not self.subscribers:
            QMessageBox.information(self, "Exportar", "No hay suscriptores para exportar.")
            return
        path, _ = QMessageBox.getSaveFileName(self, "Exportar CSV", "suscriptores.csv", "CSV (*.csv)")
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Email", "Fecha de suscripción"])
                for s in self.subscribers:
                    writer.writerow([s.get("email", ""), s.get("subscribed_at", "")])
            QMessageBox.information(self, "Exportado", f"Exportados {len(self.subscribers)} emails a CSV.")

    def _export_json(self):
        if not self.subscribers:
            QMessageBox.information(self, "Exportar", "No hay suscriptores para exportar.")
            return
        import json
        path, _ = QMessageBox.getSaveFileName(self, "Exportar JSON", "suscriptores.json", "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"subscribers": self.subscribers}, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Exportado", f"Exportados {len(self.subscribers)} emails a JSON.")
