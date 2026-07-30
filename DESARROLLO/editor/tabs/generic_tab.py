"""
CONTEXTO: Pestaña genérica para edición de contenido simple
          (título + cuerpo). Usada por el editor configurado
          con site_config.json para páginas de tipo 'content'.
          Guarda tanto en data/*.json como en el .html real.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 23
[002] UI / FORM              - línea 36
[003] HTML GENERATION        - línea 75
[004] CRUD / GUARDAR         - línea 100
"""
import json
import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QInputDialog,
)
from PySide6.QtCore import Qt

EDITOR_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE_ROOT = os.path.join(EDITOR_ROOT, "BM WEB")
TEMPLATE_DIR = os.path.join(EDITOR_ROOT, "site_template")
SITE_CONFIG_PATH = os.path.join(EDITOR_ROOT, "site_config.json")


# [001] IMPORTS / CLASE
class GenericTab(QWidget):
    def __init__(self, page_config, refresh_callback=None, parent=None):
        super().__init__(parent)
        self._page_config = page_config
        self._refresh_callback = refresh_callback
        self._file_name = page_config.get("file", "index.html")
        self._site_config = self._load_site_config()
        self._setup_ui()
        self._load_data()

    def _load_site_config(self):
        if os.path.exists(SITE_CONFIG_PATH):
            try:
                with open(SITE_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    # [002] UI / FORM
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        label = self._page_config.get("label", self._file_name)
        header = QLabel(label)
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Título de la p\u00e1gina")
        layout.addWidget(self.title_input)

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Contenido (acepta HTML)")
        self.body_input.setMaximumHeight(200)
        layout.addWidget(self.body_input)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self._save)
        self.refresh_btn = QPushButton("Recargar")
        self.refresh_btn.clicked.connect(self._load_data)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Campo", "Valor", "Acci\u00f3n"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    # [003] HTML GENERATION
    def _template_path(self):
        return os.path.join(TEMPLATE_DIR, "page_template.html")

    def _read_template(self):
        path = self._template_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def _nav_links_html(self):
        pages = self._site_config.get("pages", [])
        links = []
        for p in pages:
            f = p.get("file", "")
            label = p.get("label", f.replace(".html", "").replace("_", " ").title())
            active = " class=\"active\"" if f == self._file_name else ""
            links.append(f"<a href=\"{f}\"{active}>{label}</a>")
        return "\n            ".join(links)

    def _generate_html(self, title, body):
        tmpl = self._read_template()
        site_name = self._site_config.get("site_name", "Mi Sitio")
        site_title = self._site_config.get("site_title", site_name)
        nav = self._nav_links_html()
        body_html = f"<h2>{title}</h2>\n<div class=\"content-body\">{body}</div>"
        if tmpl:
            html = tmpl
            html = html.replace("<!-- SITE_TITLE -->", site_title)
            html = html.replace("<!-- PAGE_TITLE -->", title)
            html = html.replace("<!-- NAV_LINKS -->", nav)
            html = html.replace("<!-- CONTENT -->", body_html)
        else:
            html = (
                "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n"
                "<meta charset=\"UTF-8\">\n"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
                f"<title>{site_title} — {title}</title>\n"
                "<link rel=\"stylesheet\" href=\"assets/css/styles.css\">\n"
                "</head>\n<body>\n"
                f"<header><h1>{site_title}</h1><nav>\n            {nav}\n</nav></header>\n"
                f"<main>\n{body_html}\n</main>\n"
                "</body>\n</html>"
            )
        return html

    def _html_file_path(self):
        return os.path.join(SITE_ROOT, self._file_name)

    def _extract_from_html(self):
        path = self._html_file_path()
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        h2_m = re.search(r"<h2>(.*?)</h2>", html)
        body_m = re.search(r'<div class="content-body">(.*?)</div>', html, re.DOTALL)
        return {
            "title": h2_m.group(1).strip() if h2_m else "",
            "body": body_m.group(1).strip() if body_m else "",
        }

    # [004] CRUD / GUARDAR
    def _data_file(self):
        return os.path.join(SITE_ROOT, "data", self._file_name.replace(".html", ".json"))

    def _load_data(self):
        path = self._data_file()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            extracted = self._extract_from_html()
            if extracted:
                self._data = extracted
            else:
                self._data = {"title": "", "body": ""}
        self.title_input.setText(self._data.get("title", ""))
        self.body_input.setPlainText(self._data.get("body", ""))
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(0)
        for key, val in self._data.items():
            if key in ("title", "body"):
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(str(val)))
            del_btn = QPushButton("Eliminar")
            del_btn.clicked.connect(lambda _, r=row: self._remove_field(r))
            self.table.setCellWidget(row, 2, del_btn)

    def _add_field(self):
        field, ok = QInputDialog.getText(self, "Nuevo campo", "Nombre del campo:")
        if not ok or not field:
            return
        val, ok = QInputDialog.getText(self, "Valor", f"Valor para '{field}':")
        if not ok:
            return
        self._data[field] = val
        self._save()

    def _remove_field(self, row):
        key = self.table.item(row, 0).text()
        del self._data[key]
        self._save()

    def _save(self):
        self._data["title"] = self.title_input.text()
        self._data["body"] = self.body_input.toPlainText()
        data_path = self._data_file()
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        html = self._generate_html(self._data["title"], self._data["body"])
        with open(self._html_file_path(), "w", encoding="utf-8") as f:
            f.write(html)
        if self._refresh_callback:
            self._refresh_callback()
        QMessageBox.information(self, "Guardado", "P\u00e1gina guardada correctamente.")
