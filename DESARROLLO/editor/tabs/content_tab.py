"""
CONTEXTO: Tab de Pipeline de Contenido — scrapea web, genera notas
          con AI, permite editar, revisar y publicar al sitio.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / WORKER        - línea 12
[002] UI / LAYOUT             - línea 40
[003] SCRAPE & GENERATE       - línea 120
[004] EDIT & PREVIEW          - línea 180
[005] PUBLISH                 - línea 230
[006] HELPERS                 - línea 260
"""
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QFrame, QSplitter, QMessageBox,
    QProgressBar, QListWidget, QComboBox, QFileDialog,
)
from PySide6.QtCore import Qt, QThread, Signal

from services import ai_service
from services import content_scraper
from services import news_generator
from services import html_generator

ARTICLES_FILE = os.path.join(os.path.dirname(__file__), "..", "articles.json")


# [001] WORKERS
class ScrapeWorker(QThread):
    finished = Signal(dict)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        try:
            data = content_scraper.fetch_article(self.url)
            self.finished.emit(data)
        except Exception as e:
            self.finished.emit({"error": str(e), "ok": False})


class GenerateWorker(QThread):
    finished = Signal(dict)
    def __init__(self, scraped_data, topic=""):
        super().__init__()
        self.scraped_data = scraped_data
        self.topic = topic
    def run(self):
        try:
            article = news_generator.generate_news_article(self.scraped_data, self.topic)
            self.finished.emit(article)
        except Exception as e:
            self.finished.emit({"error": str(e), "ok": False})


class SearchWorker(QThread):
    finished = Signal(list)
    def __init__(self, query):
        super().__init__()
        self.query = query
    def run(self):
        try:
            results = content_scraper.search_web(self.query, num_results=8)
            self.finished.emit(results)
        except Exception:
            self.finished.emit([])


# [002] UI / LAYOUT
class ContentPipelineTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scraped = None
        self._article = None
        self._worker = None
        self._articles = self._load_articles()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QLabel("Pipeline de Contenido")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        main_split = QSplitter(Qt.Horizontal)

        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame{border:1px solid #1f2225; padding:8px;}")
        left_l = QVBoxLayout(left_panel)
        left_l.setContentsMargins(6, 6, 6, 6)

        url_lbl = QLabel("URL o búsqueda:")
        url_lbl.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif;")
        left_l.addWidget(url_lbl)

        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pegá una URL o escribí un tema...")
        url_row.addWidget(self.url_input, 1)
        left_l.addLayout(url_row)

        btn_row = QHBoxLayout()
        self.scrape_btn = QPushButton("Scrapear URL")
        self.scrape_btn.clicked.connect(self._scrape_url)
        btn_row.addWidget(self.scrape_btn)
        self.search_btn = QPushButton("Buscar en web")
        self.search_btn.clicked.connect(self._search_web)
        btn_row.addWidget(self.search_btn)
        left_l.addLayout(btn_row)

        self.search_results = QListWidget()
        self.search_results.setStyleSheet("QListWidget{border:none; background:transparent;}")
        self.search_results.itemDoubleClicked.connect(self._select_result)
        left_l.addWidget(self.search_results)

        topic_row = QHBoxLayout()
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enfoque (opcional): política, reviews, etc.")
        topic_row.addWidget(self.topic_input)
        left_l.addLayout(topic_row)

        self.gen_btn = QPushButton("Generar nota con AI")
        self.gen_btn.clicked.connect(self._generate_article)
        left_l.addWidget(self.gen_btn)

        sep = QLabel("Notas guardadas")
        sep.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif; margin-top:8px;")
        left_l.addWidget(sep)

        self.articles_list = QListWidget()
        self.articles_list.setStyleSheet("QListWidget{border:none; background:transparent;}")
        self.articles_list.itemClicked.connect(self._load_article)
        left_l.addWidget(self.articles_list)
        self._refresh_articles_list()

        left_l.addStretch()

        main_split.addWidget(left_panel)

        right_panel = QWidget()
        right_l = QVBoxLayout(right_panel)
        right_l.setContentsMargins(0, 0, 0, 0)

        preview_lbl = QLabel("Preview de la nota")
        preview_lbl.setStyleSheet("color:#7a6346; font-family:'Cinzel',serif;")
        right_l.addWidget(preview_lbl)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Título de la nota...")
        self.title_edit.setStyleSheet("font-family:'Cinzel',serif; font-size:14px; padding:8px;")
        right_l.addWidget(self.title_edit)

        self.subtitle_edit = QLineEdit()
        self.subtitle_edit.setPlaceholderText("Bajada...")
        self.subtitle_edit.setStyleSheet("font-style:italic; padding:6px;")
        right_l.addWidget(self.subtitle_edit)

        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText("Cuerpo de la nota...")
        self.body_edit.setStyleSheet("QTextEdit{font-family:'Inter',sans-serif; padding:8px;}")
        right_l.addWidget(self.body_edit, 1)

        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (separados por coma)...")
        right_l.addWidget(self.tags_edit)

        pub_row = QHBoxLayout()
        self.save_btn = QPushButton("Guardar borrador")
        self.save_btn.clicked.connect(self._save_article)
        pub_row.addWidget(self.save_btn)
        self.publish_btn = QPushButton("Publicar al sitio")
        self.publish_btn.setStyleSheet("QPushButton{background:#4a0f0d; color:#e8e6df;}")
        self.publish_btn.clicked.connect(self._publish_article)
        pub_row.addWidget(self.publish_btn)
        right_l.addLayout(pub_row)

        main_split.addWidget(right_panel)
        main_split.setSizes([300, 500])
        layout.addWidget(main_split, 1)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet("QProgressBar{border:1px solid #1f2225; height:3px;} QProgressBar::chunk{background:#4a0f0d;}")
        layout.addWidget(self.progress)

    # [003] SCRAPE & GENERATE
    def _scrape_url(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if not url.startswith("http"):
            url = "https://" + url
        self.progress.setVisible(True)
        self.scrape_btn.setEnabled(False)
        self.scrape_btn.setText("Scrapeando...")
        worker = ScrapeWorker(url)
        worker.finished.connect(self._on_scraped)
        worker.start()
        self._worker = worker

    def _on_scraped(self, data):
        self.progress.setVisible(False)
        self.scrape_btn.setEnabled(True)
        self.scrape_btn.setText("Scrapear URL")
        if not data.get("ok"):
            QMessageBox.warning(self, "Error", data.get("error", "Error al scrapear"))
            return
        self._scraped = data
        self.search_results.clear()
        self.search_results.addItem(f"[Scrapeado] {data.get('title', 'Sin título')}")
        self.search_results.addItem(f"  URL: {data.get('url', '')}")
        self.search_results.addItem(f"  Imágenes: {len(data.get('images', []))}")

    def _search_web(self):
        query = self.url_input.text().strip()
        if not query:
            return
        self.progress.setVisible(True)
        self.search_btn.setEnabled(False)
        worker = SearchWorker(query)
        worker.finished.connect(self._on_search_results)
        worker.start()
        self._worker = worker

    def _on_search_results(self, results):
        self.progress.setVisible(False)
        self.search_btn.setEnabled(True)
        self.search_results.clear()
        if not results:
            self.search_results.addItem("Sin resultados")
            return
        for r in results:
            self.search_results.addItem(f"{r['title'][:60]}  →  {r['url']}")

    def _select_result(self, item):
        text = item.text()
        if "→" in text:
            url = text.split("→")[-1].strip()
            self.url_input.setText(url)

    def _generate_article(self):
        url = self.url_input.text().strip()
        topic = self.topic_input.text().strip()
        if not url and not self._scraped:
            QMessageBox.information(self, "Datos", "Escribí una URL o scrapeá primero.")
            return
        self.progress.setVisible(True)
        self.gen_btn.setEnabled(False)
        if self._scraped and self._scraped.get("url") == url:
            worker = GenerateWorker(self._scraped, topic)
        else:
            if not url.startswith("http"):
                url = "https://" + url
            scraped = content_scraper.fetch_article(url)
            worker = GenerateWorker(scraped, topic)
        worker.finished.connect(self._on_article_generated)
        worker.start()
        self._worker = worker

    def _on_article_generated(self, article):
        self.progress.setVisible(False)
        self.gen_btn.setEnabled(True)
        if not article.get("ok"):
            QMessageBox.warning(self, "Error AI", article.get("error", "No se pudo generar"))
            if article.get("raw"):
                self.body_edit.setPlainText(article["raw"])
            return
        self._article = article
        self.title_edit.setText(article.get("titulo", ""))
        self.subtitle_edit.setText(article.get("bajada", ""))
        self.body_edit.setPlainText(article.get("cuerpo", ""))
        self.tags_edit.setText(", ".join(article.get("tags", [])))

    # [004] EDIT & PREVIEW
    def _save_article(self):
        article = self._get_current_article()
        if not article.get("titulo"):
            QMessageBox.information(self, "Datos", "El título es obligatorio.")
            return
        article["guardado"] = datetime.now().isoformat()
        exists = False
        for i, a in enumerate(self._articles):
            if a.get("titulo") == article.get("titulo"):
                self._articles[i] = article
                exists = True
                break
        if not exists:
            self._articles.append(article)
        self._save_articles_file()
        self._refresh_articles_list()
        QMessageBox.information(self, "Guardado", "Nota guardada como borrador.")

    def _load_article(self, item):
        idx = self.articles_list.row(item)
        if idx < 0 or idx >= len(self._articles):
            return
        article = self._articles[idx]
        self.title_edit.setText(article.get("titulo", ""))
        self.subtitle_edit.setText(article.get("bajada", ""))
        self.body_edit.setPlainText(article.get("cuerpo", ""))
        self.tags_edit.setText(", ".join(article.get("tags", [])))
        self._article = article

    # [005] PUBLISH
    def _publish_article(self):
        article = self._get_current_article()
        if not article.get("titulo") or not article.get("cuerpo"):
            QMessageBox.information(self, "Datos", "Completá título y cuerpo.")
            return
        resp = QMessageBox.question(
            self, "Publicar",
            f"¿Publicar '{article['titulo']}' en el sitio?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return

        try:
            html_generator.add_news({
                "titulo": article["titulo"],
                "bajada": article.get("bajada", ""),
                "cuerpo": article["cuerpo"],
                "imagen": article.get("imagen_url", ""),
                "tags": article.get("tags", []),
                "fecha": article.get("fecha", datetime.now().strftime("%Y-%m-%d")),
            })
            self.progress.setVisible(True)
            from services.site_publisher import publish
            result = publish(f"Nota publicada: {article['titulo']}")
            self.progress.setVisible(False)
            if result.get("ok"):
                QMessageBox.information(self, "Publicado", "Nota publicada al sitio correctamente.")
            else:
                QMessageBox.warning(self, "Error", result.get("error", "Error al publicar"))
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.warning(self, "Error", str(e))

    # [006] HELPERS
    def _get_current_article(self):
        return {
            "titulo": self.title_edit.text().strip(),
            "bajada": self.subtitle_edit.text().strip(),
            "cuerpo": self.body_edit.toPlainText().strip(),
            "tags": [t.strip() for t in self.tags_edit.text().split(",") if t.strip()],
            "imagen_url": self._article.get("imagen_url", "") if self._article else "",
            "fuente_url": self._article.get("fuente_url", "") if self._article else "",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
        }

    def _load_articles(self):
        if os.path.exists(ARTICLES_FILE):
            try:
                with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_articles_file(self):
        os.makedirs(os.path.dirname(ARTICLES_FILE), exist_ok=True)
        with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
            json.dump(self._articles, f, ensure_ascii=False, indent=2)

    def _refresh_articles_list(self):
        self.articles_list.clear()
        for a in self._articles:
            status = "📝" if not a.get("publicado") else "✅"
            self.articles_list.addItem(f"{status} {a.get('titulo', 'Sin título')}")
