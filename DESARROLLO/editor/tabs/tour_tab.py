"""
CONTEXTO: Pestaña de gestión de fechas de tour. CRUD completo con
          tabla editable, persistencia en js.js (FECHAS[]). Soporta
          búsqueda de Google Maps, adjuntar fotos desde disco,
          descripción de la fecha y transporte.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 14
[002] UI / FORM / TABLA     - línea 28
[003] CRUD                  - línea 110
[004] HELPERS               - línea 155
"""
import os
import shutil
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QFrame, QDateEdit,
)
from PySide6.QtCore import Qt, QDate
from services.html_generator import get_fechas, save_fechas, SITE_ROOT

TOUR_PHOTOS_DIR = os.path.join(SITE_ROOT, "assets", "tour")
ORIGIN_DEFAULT = "Buenos Aires, Argentina"


# [001] IMPORTS / CLASE
class TourTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        os.makedirs(TOUR_PHOTOS_DIR, exist_ok=True)
        self._setup_ui()
        self.load_data()

    # [002] UI / FORM / TABLA
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QLabel("Fechas de Tour")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        form_l = QVBoxLayout()
        form_l.setSpacing(6)

        row1 = QHBoxLayout()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate(2026, 1, 1))
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setStyleSheet("color:#9aa0a6;")
        self.date_input.setToolTip("Fecha en que se realiza el show (NO es la fecha de hoy)")
        self.place_input = QLineEdit()
        self.place_input.setPlaceholderText("Lugar *")
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Ciudad")
        row1.addWidget(QLabel("Fecha del show:"))
        row1.addWidget(self.date_input)
        row1.addWidget(self.place_input)
        row1.addWidget(self.city_input)
        form_l.addLayout(row1)

        row2 = QHBoxLayout()
        self.tickets_input = QLineEdit()
        self.tickets_input.setPlaceholderText("Link tickets (vacío = WhatsApp)")
        row2.addWidget(self.tickets_input)
        form_l.addLayout(row2)

        maps_row = QHBoxLayout()
        self.mapa_search = QLineEdit()
        self.mapa_search.setPlaceholderText("Buscar dirección en Google Maps (ej: Av. Savedra 1234, Quilmes)")
        self.mapa_search.returnPressed.connect(self._search_maps)
        self.mapa_btn = QPushButton("Buscar Maps")
        self.mapa_btn.clicked.connect(self._search_maps)
        self.mapa_input = QLineEdit()
        self.mapa_input.setPlaceholderText("URL embed Google Maps (se completa automáticamente)")
        maps_row.addWidget(self.mapa_search)
        maps_row.addWidget(self.mapa_btn)
        maps_row.addWidget(self.mapa_input)
        form_l.addLayout(maps_row)

        fotos_row = QHBoxLayout()
        self.fotos_label = QLabel("Fotos: 0 adjuntas")
        self.fotos_label.setStyleSheet("color:#7a6346; font-size:11px;")
        self.add_photo_btn = QPushButton("+ Adjuntar fotos")
        self.add_photo_btn.clicked.connect(self._add_photos)
        self.clear_photos_btn = QPushButton("Limpiar fotos")
        self.clear_photos_btn.clicked.connect(self._clear_photos)
        fotos_row.addWidget(self.fotos_label)
        fotos_row.addWidget(self.add_photo_btn)
        fotos_row.addWidget(self.clear_photos_btn)
        form_l.addLayout(fotos_row)

        self.transporte_input = QLineEdit()
        self.transporte_input.setPlaceholderText("Cómo llegar: colectivos, tren, etc.")
        self.transporte_btn = QPushButton("Buscar traslado en Maps")
        self.transporte_btn.clicked.connect(self._search_transport)
        trans_row = QHBoxLayout()
        trans_row.addWidget(self.transporte_input)
        trans_row.addWidget(self.transporte_btn)
        form_l.addLayout(trans_row)

        self.origin_input = QLineEdit()
        self.origin_input.setPlaceholderText("Punto de partida para buscar traslado (ej: Buenos Aires, Quilmes)")
        self.origin_input.setText(ORIGIN_DEFAULT)
        form_l.addWidget(self.origin_input)

        desc_label = QLabel("Descripción de la fecha:")
        desc_label.setStyleSheet("color:#9aa0a6; font-size:11px;")
        form_l.addWidget(desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descripción del show: precio, hora, bandas invitadas, etc.")
        self.desc_input.setMaximumHeight(80)
        form_l.addWidget(self.desc_input)

        self.add_btn = QPushButton("Agregar fecha")
        self.add_btn.clicked.connect(self._add)
        form_l.addWidget(self.add_btn)
        layout.addLayout(form_l)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#1f2225;")
        layout.addWidget(sep)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Fecha", "Lugar", "Ciudad", "Extras", "Fotos", "Acción"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.clicked.connect(self._on_select)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar cambios")
        self.save_btn.clicked.connect(self._save)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)

    # [003] CRUD
    def load_data(self):
        self.fechas = get_fechas()
        self._selected_photos = []
        self.table.setRowCount(len(self.fechas))
        for i, f in enumerate(self.fechas):
            dia = f.get("dia", "")
            mes = f.get("mes", "")
            anio = f.get("anio", "")
            fecha_str = f"{dia}/{mes}/{anio}" if mes else dia
            self.table.setItem(i, 0, QTableWidgetItem(fecha_str))
            self.table.setItem(i, 1, QTableWidgetItem(f.get("lugar", "")))
            self.table.setItem(i, 2, QTableWidgetItem(f.get("ciudad", "")))
            extras = []
            if f.get("link"): extras.append("Tickets")
            if f.get("mapa"): extras.append("Mapa")
            if f.get("transporte"): extras.append("Transporte")
            if f.get("descripcion"): extras.append("Descripción")
            self.table.setItem(i, 3, QTableWidgetItem(" | ".join(extras)))
            fotos_count = len(f.get("fotos", []))
            self.table.setItem(i, 4, QTableWidgetItem(f"{fotos_count} foto(s)" if fotos_count else ""))
            del_btn = QPushButton("Eliminar")
            del_btn.clicked.connect(lambda _, row=i: self._delete(row))
            self.table.setCellWidget(i, 5, del_btn)
        self.fotos_label.setText(f"Fotos: {len(self._selected_photos)} adjuntas")

    def _on_select(self, index):
        row = index.row()
        if row < len(self.fechas):
            f = self.fechas[row]
            try:
                dia = int(f.get("dia", "1"))
                mes_map = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
                           "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12}
                mes = mes_map.get(f.get("mes", "ENE"), 1)
                anio = int(f.get("anio", "2026"))
                self.date_input.setDate(QDate(anio, mes, dia))
            except (ValueError, TypeError):
                self.date_input.setDate(QDate(2026, 1, 1))
            self.place_input.setText(f.get("lugar", ""))
            self.city_input.setText(f.get("ciudad", ""))
            self.tickets_input.setText(f.get("link", ""))
            self.mapa_input.setText(f.get("mapa", ""))
            self.transporte_input.setText(f.get("transporte", ""))
            self.desc_input.setPlainText(f.get("descripcion", ""))
            self._selected_photos = list(f.get("fotos", []))
            self.fotos_label.setText(f"Fotos: {len(self._selected_photos)} adjuntas")
            self.mapa_search.clear()

    def _add(self):
        d = self.date_input.date()
        lugar = self.place_input.text().strip()
        if not lugar:
            QMessageBox.warning(self, "Error", "El lugar es obligatorio.")
            return
        self.fechas.append({
            "dia": str(d.day()).zfill(2),
            "mes": d.toString("MMM").upper(),
            "anio": str(d.year()),
            "lugar": lugar,
            "ciudad": self.city_input.text().strip(),
            "link": self.tickets_input.text().strip(),
            "fotos": list(self._selected_photos),
            "mapa": self.mapa_input.text().strip(),
            "transporte": self.transporte_input.text().strip(),
            "descripcion": self.desc_input.toPlainText().strip(),
        })
        save_fechas(self.fechas)
        self._clear_form()
        self.load_data()

    def _delete(self, row):
        confirm = QMessageBox.question(
            self, "Eliminar", f"¿Eliminar la fecha en {self.fechas[row].get('lugar', '')}?",
        )
        if confirm == QMessageBox.Yes:
            self.fechas.pop(row)
            save_fechas(self.fechas)
            self.load_data()

    def _save(self):
        save_fechas(self.fechas)
        QMessageBox.information(self, "Guardado", "Fechas guardadas correctamente.")

    def _clear_form(self):
        self.date_input.setDate(QDate(2026, 1, 1))
        self.place_input.clear()
        self.city_input.clear()
        self.tickets_input.clear()
        self.mapa_input.clear()
        self.mapa_search.clear()
        self.transporte_input.clear()
        self.desc_input.clear()
        self._selected_photos = []
        self.fotos_label.setText("Fotos: 0 adjuntas")

    # [004] HELPERS
    def _search_maps(self):
        query = self.mapa_search.text().strip()
        if not query:
            return
        embed_url = "https://maps.google.com/maps?q=" + query.replace(" ", "+") + "&output=embed"
        self.mapa_input.setText(embed_url)

    def _add_photos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Adjuntar fotos promocionales", "",
            "Imágenes (*.jpg *.jpeg *.png *.webp);;Todos (*)"
        )
        if not files:
            return
        copied = 0
        for src in files:
            fname = os.path.basename(src)
            dst = os.path.join(TOUR_PHOTOS_DIR, fname)
            if os.path.exists(dst):
                base, ext = os.path.splitext(fname)
                i = 1
                while os.path.exists(os.path.join(TOUR_PHOTOS_DIR, f"{base}_{i}{ext}")):
                    i += 1
                dst = os.path.join(TOUR_PHOTOS_DIR, f"{base}_{i}{ext}")
                fname = f"{base}_{i}{ext}"
            shutil.copy2(src, dst)
            rel = "assets/tour/" + fname
            if rel not in self._selected_photos:
                self._selected_photos.append(rel)
                copied += 1
        self.fotos_label.setText(f"Fotos: {len(self._selected_photos)} adjuntas")

    def _clear_photos(self):
        self._selected_photos = []
        self.fotos_label.setText("Fotos: 0 adjuntas")

    def _search_transport(self):
        destino = self.place_input.text().strip()
        ciudad = self.city_input.text().strip()
        query = destino + (", " + ciudad if ciudad else "")
        if not query:
            QMessageBox.information(self, "Traslado", "Primero ingresá el lugar de la fecha.")
            return
        origen = self.origin_input.text().strip() or ORIGIN_DEFAULT
        url = "https://www.google.com/maps/dir/" + origen.replace(" ", "+") + "/" + query.replace(" ", "+") + "/data=!3m1!4b1!4m2!4m1!3e3"
        webbrowser.open(url)
