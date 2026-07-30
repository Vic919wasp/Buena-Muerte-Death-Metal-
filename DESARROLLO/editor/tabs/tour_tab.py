"""
CONTEXTO: Pestaña de gestión de fechas de tour. CRUD completo con
           tabla editable, persistencia en js.js (FECHAS[]). Soporta
           búsqueda de Google Maps, adjuntar fotos desde disco,
           descripción de la fecha y transporte.
           El formulario de alta/edición se abre en un QDialog flotante
           para dejar más espacio a la lista de fechas.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CONSTANTES   - línea 12
[002] TOUR DATE DIALOG       - línea 36
[003] TOUR TAB               - línea 224
[004] HELPERS DIALOG         - línea 176
"""
import os
import shutil
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QDateEdit, QDialog, QDialogButtonBox,
    QFormLayout,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QMenu
from services.html_generator import get_fechas, save_fechas, SITE_ROOT

TOUR_PHOTOS_DIR = os.path.join(SITE_ROOT, "assets", "tour")
ORIGIN_DEFAULT = "Buenos Aires, Argentina"
MES_MAP = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
           "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12,
           "JAN": 1, "APR": 4, "AUG": 8, "DEC": 12}
MES_NOMBRES = ("", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
               "JUL", "AGO", "SEP", "OCT", "NOV", "DIC")


# [002] TOUR DATE DIALOG
class TourDateDialog(QDialog):
    def __init__(self, parent=None, fecha=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar fecha" if fecha is None else "Editar fecha")
        self.setMinimumWidth(520)
        self._fecha = fecha
        self._selected_photos = []
        self._setup_ui()
        if fecha is not None:
            self._load_fecha(fecha)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(6)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate(2026, 1, 1))
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setStyleSheet("color:#9aa0a6;")
        form.addRow("Fecha del show:", self.date_input)

        self.place_input = QLineEdit()
        self.place_input.setPlaceholderText("Lugar *")
        form.addRow("Lugar:", self.place_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Ciudad")
        form.addRow("Ciudad:", self.city_input)

        self.tickets_input = QLineEdit()
        self.tickets_input.setPlaceholderText("Link tickets (vacío = WhatsApp)")
        form.addRow("Tickets:", self.tickets_input)

        maps_row = QHBoxLayout()
        self.mapa_search = QLineEdit()
        self.mapa_search.setPlaceholderText("Ej: Av. Savedra 1234, Quilmes")
        self.mapa_search.returnPressed.connect(self._search_maps)
        self.mapa_btn = QPushButton("Buscar")
        self.mapa_btn.clicked.connect(self._search_maps)
        self.mapa_input = QLineEdit()
        self.mapa_input.setPlaceholderText("URL embed")
        maps_row.addWidget(self.mapa_search)
        maps_row.addWidget(self.mapa_btn)
        maps_row.addWidget(self.mapa_input)

        maps_label = QLabel("Google Maps:")
        maps_label.setStyleSheet("color:#9aa0a6;")
        form.addRow(maps_label, maps_row)

        fotos_row = QHBoxLayout()
        self.fotos_label = QLabel("0 adjuntas")
        self.fotos_label.setStyleSheet("color:#7a6346; font-size:11px;")
        self.add_photo_btn = QPushButton("+ Adjuntar fotos")
        self.add_photo_btn.clicked.connect(self._add_photos)
        self.clear_photos_btn = QPushButton("Limpiar")
        self.clear_photos_btn.clicked.connect(self._clear_photos)
        fotos_row.addWidget(self.fotos_label)
        fotos_row.addWidget(self.add_photo_btn)
        fotos_row.addWidget(self.clear_photos_btn)

        fotos_label_w = QLabel("Fotos:")
        fotos_label_w.setStyleSheet("color:#9aa0a6;")
        form.addRow(fotos_label_w, fotos_row)

        self.transporte_input = QLineEdit()
        self.transporte_input.setPlaceholderText("Colectivos, tren, etc.")
        self.transporte_btn = QPushButton("Maps")
        self.transporte_btn.clicked.connect(self._search_transport)
        trans_row = QHBoxLayout()
        trans_row.addWidget(self.transporte_input)
        trans_row.addWidget(self.transporte_btn)

        self.origin_input = QLineEdit()
        self.origin_input.setPlaceholderText("Punto de partida")
        self.origin_input.setText(ORIGIN_DEFAULT)
        trans_row.addWidget(self.origin_input)

        trans_label = QLabel("Transporte:")
        trans_label.setStyleSheet("color:#9aa0a6;")
        form.addRow(trans_label, trans_row)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Precio, hora, bandas invitadas, etc.")
        self.desc_input.setMaximumHeight(100)
        desc_label = QLabel("Descripción:")
        desc_label.setStyleSheet("color:#9aa0a6;")
        form.addRow(desc_label, self.desc_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_fecha(self, f):
        try:
            dia = int(f.get("dia", "1"))
            mes = MES_MAP.get(f.get("mes", "ENE"), 1)
            anio = int(f.get("anio", "2026"))
            self.date_input.setDate(QDate(anio, mes, dia))
        except (ValueError, TypeError):
            pass
        self.place_input.setText(f.get("lugar", ""))
        self.city_input.setText(f.get("ciudad", ""))
        self.tickets_input.setText(f.get("link", ""))
        self.mapa_input.setText(f.get("mapa", ""))
        self.transporte_input.setText(f.get("transporte", ""))
        self.desc_input.setPlainText(f.get("descripcion", ""))
        self._selected_photos = list(f.get("fotos", []))
        self.fotos_label.setText(f"{len(self._selected_photos)} adjuntas")

    def _accept(self):
        lugar = self.place_input.text().strip()
        if not lugar:
            QMessageBox.warning(self, "Error", "El lugar es obligatorio.")
            return
        d = self.date_input.date()
        self._result = {
            "dia": str(d.day()).zfill(2),
            "mes": MES_NOMBRES[d.month()],
            "anio": str(d.year()),
            "lugar": lugar,
            "ciudad": self.city_input.text().strip(),
            "link": self.tickets_input.text().strip(),
            "fotos": list(self._selected_photos),
            "mapa": self.mapa_input.text().strip(),
            "transporte": self.transporte_input.text().strip(),
            "descripcion": self.desc_input.toPlainText().strip(),
        }
        self.accept()

    def result(self):
        return getattr(self, "_result", None)

    # [004] HELPERS DIALOG
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
        self.fotos_label.setText(f"{len(self._selected_photos)} adjuntas")

    def _clear_photos(self):
        self._selected_photos = []
        self.fotos_label.setText("0 adjuntas")

    def _search_transport(self):
        destino = self.place_input.text().strip()
        ciudad = self.city_input.text().strip()
        query = destino + (", " + ciudad if ciudad else "")
        if not query:
            QMessageBox.information(self, "Traslado", "Primero ingresá el lugar de la fecha.")
            return
        origen = self.origin_input.text().strip() or ORIGIN_DEFAULT
        url = ("https://www.google.com/maps/dir/" + origen.replace(" ", "+") + "/"
               + query.replace(" ", "+") + "/data=!3m1!4b1!4m2!4m1!3e3")
        webbrowser.open(url)


# [003] TOUR TAB
class TourTab(QWidget):
    def __init__(self, refresh_callback=None, parent=None):
        super().__init__(parent)
        self._refresh_callback = refresh_callback
        os.makedirs(TOUR_PHOTOS_DIR, exist_ok=True)
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QLabel("Fechas de Tour")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("+ Añadir fecha")
        self.add_btn.clicked.connect(self._add_date)
        self.save_btn = QPushButton("Guardar cambios")
        self.save_btn.clicked.connect(self._save)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_row.addWidget(self.add_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Fecha", "Lugar", "Ciudad", "Extras", "Fotos"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_context_menu)
        row_header = self.table.verticalHeader()
        row_header.setSectionsMovable(True)
        row_header.setSectionsClickable(True)
        row_header.setToolTip("Arrastrá una fila para cambiar el orden de las fechas")
        row_header.sectionMoved.connect(self._on_row_moved)
        layout.addWidget(self.table, stretch=1)  # que la tabla ocupe todo el espacio disponible

    def load_data(self):
        self.fechas = get_fechas()
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

    def _on_row_moved(self, logical_index, old_visual_index, new_visual_index):
        row_header = self.table.verticalHeader()
        order = [row_header.logicalIndex(i) for i in range(self.table.rowCount())]
        self.fechas = [self.fechas[i] for i in order]

        row_header.blockSignals(True)
        for visual_index in range(self.table.rowCount()):
            current_visual = row_header.visualIndex(visual_index)
            if current_visual != visual_index:
                row_header.moveSection(current_visual, visual_index)
        row_header.blockSignals(False)

        save_fechas(self.fechas)
        self.load_data()
        if self._refresh_callback:
            self._refresh_callback()

    def _add_date(self):
        dlg = TourDateDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.result()
            if data:
                self.fechas.append(data)
                save_fechas(self.fechas)
                self.load_data()
                if self._refresh_callback:
                    self._refresh_callback()

    def _edit_date(self, row):
        f = self.fechas[row]
        dlg = TourDateDialog(self, fecha=f)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.result()
            if data:
                self.fechas[row] = data
                save_fechas(self.fechas)
                self.load_data()
                if self._refresh_callback:
                    self._refresh_callback()

    def _on_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        if row >= len(self.fechas):
            return
        lugar = self.fechas[row].get("lugar", f"fila {row+1}")
        menu = QMenu(self)
        edit_action = menu.addAction(f"Editar {lugar}")
        edit_action.triggered.connect(lambda: self._edit_date(row))
        menu.addSeparator()
        del_action = menu.addAction(f"Eliminar {lugar}")
        del_action.triggered.connect(lambda: self._delete(row))
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _delete(self, row):
        confirm = QMessageBox.question(
            self, "Eliminar", f"¿Eliminar la fecha en {self.fechas[row].get('lugar', '')}?",
        )
        if confirm == QMessageBox.Yes:
            self.fechas.pop(row)
            save_fechas(self.fechas)
            self.load_data()
            if self._refresh_callback:
                self._refresh_callback()

    def _save(self):
        save_fechas(self.fechas)
        QMessageBox.information(self, "Guardado", "Fechas guardadas correctamente.")
        if self._refresh_callback:
            self._refresh_callback()
