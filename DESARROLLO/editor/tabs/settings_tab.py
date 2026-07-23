"""
CONTEXTO: Pestaña de configuración y publicación. Permite configurar
          rutas, ver estado del repo y publicar cambios.
ÍNDICE DE NAVEGACIÓN
[001] IMPORTS / CLASE       - línea 12
[002] UI                    - línea 25
[003] ACCIONES              - línea 70
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QMessageBox,
)
from PySide6.QtCore import Qt
from services import site_publisher


# [001] IMPORTS / CLASE
class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._refresh_status()

    # [002] UI
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        header = QLabel("Configuración y Publicación")
        header.setStyleSheet("font-family:'Cinzel',serif; font-size:18px; color:#c8ccd0;")
        layout.addWidget(header)

        status_label = QLabel("Estado del repositorio:")
        status_label.setStyleSheet("color:#9aa0a6;")
        layout.addWidget(status_label)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        layout.addWidget(self.status_text)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Actualizar estado")
        self.refresh_btn.clicked.connect(self._refresh_status)
        btn_row.addWidget(self.refresh_btn)
        layout.addLayout(btn_row)

        pub_label = QLabel("Publicar cambios:")
        pub_label.setStyleSheet("color:#9aa0a6; margin-top:15px;")
        layout.addWidget(pub_label)

        msg_row = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Mensaje del commit (opcional)")
        msg_row.addWidget(self.msg_input)
        self.publish_btn = QPushButton("Publicar (git push)")
        self.publish_btn.setStyleSheet("background:#4a0f0d; color:#e8e6df; padding:8px 16px;")
        self.publish_btn.clicked.connect(self._publish)
        msg_row.addWidget(self.publish_btn)
        layout.addLayout(msg_row)

        log_label = QLabel("Últimos commits:")
        log_label.setStyleSheet("color:#9aa0a6; margin-top:15px;")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        layout.addWidget(self.log_text)

    # [003] ACCIONES
    def _refresh_status(self):
        status = site_publisher.get_status()
        if "error" in status:
            self.status_text.setPlainText(f"Error: {status['error']}")
        elif status["changed"] == 0:
            self.status_text.setPlainText("Working tree limpio — no hay cambios pendientes.")
        else:
            files = "\n".join(status["files"][:20])
            self.status_text.setPlainText(f"{status['changed']} archivos modificados:\n{files}")

        log = site_publisher.get_log(5)
        if log:
            self.log_text.setPlainText("\n".join(log))
        else:
            self.log_text.setPlainText("No hay commits recientes.")

    def _publish(self):
        confirm = QMessageBox.question(
            self,
            "Publicar",
            "¿Publicar todos los cambios al sitio?\nEsto ejecutará git push.",
        )
        if confirm != QMessageBox.Yes:
            return
        self.publish_btn.setEnabled(False)
        self.publish_btn.setText("Publicando...")
        from PySide6.QtCore import QThread, Signal

        class PublishWorker(QThread):
            finished = Signal(bool, str)

            def run(self):
                msg = self.msg_input.text().strip() if hasattr(self, 'msg_input') else None
                ok, text = site_publisher.publish(msg)
                self.finished.emit(ok, text)

        worker = PublishWorker()
        worker.msg_input = self.msg_input
        worker.finished.connect(self._on_publish_done)
        worker.start()
        self._worker = worker

    def _on_publish_done(self, ok, text):
        self.publish_btn.setEnabled(True)
        self.publish_btn.setText("Publicar (git push)")
        if ok:
            QMessageBox.information(self, "Publicado", text)
        else:
            QMessageBox.critical(self, "Error", text)
        self._refresh_status()
