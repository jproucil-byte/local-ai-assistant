import sys
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QPlainTextEdit, QLineEdit, QCheckBox,
    QDialog, QFormLayout, QMessageBox)
from .config import Settings
from .ollama_client import chat, local_endpoint
from .screen import capture_primary_screen

SYSTEM_PROMPT = ('You are Local AI Assistant, a privacy-focused desktop advisor. '
                 'Answer in the language of the user. You may interpret screenshots, '
                 'but only receive a single snapshot when the user attaches one. '
                 'You do not see a live screen. Never claim to see the current screen '
                 'without an attached screenshot. '
                 'You cannot click, type, edit files, execute commands, or browse the web. '
                 'Never claim to have performed an action. If the image is unclear, say so.')

class Worker(QObject):
    finished = Signal(str)
    failed = Signal(str)
    def __init__(self, endpoint, model, messages, screenshot):
        super().__init__()
        self.endpoint, self.model = endpoint, model
        self.messages, self.screenshot = messages, screenshot
    @Slot()
    def run(self):
        try:
            self.finished.emit(chat(self.endpoint, self.model, self.messages, self.screenshot))
        except Exception as exc:
            self.failed.emit(f'{type(exc).__name__}: {exc}')

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        form = QFormLayout(self)
        self.model = QLineEdit(settings.model)
        self.endpoint = QLineEdit(settings.endpoint)
        self.endpoint.setToolTip('Address of Ollama on this computer. 127.0.0.1 means this computer; 11434 is its service port.')
        self.on_top = QCheckBox()
        self.on_top.setChecked(settings.always_on_top)
        form.addRow('Ollama model', self.model)
        form.addRow('Local endpoint', self.endpoint)
        endpoint_hint = QLabel('Ollama runs on this computer. Usually no change is needed.')
        endpoint_hint.setWordWrap(True)
        form.addRow(endpoint_hint)
        form.addRow('Always on top', self.on_top)
        save = QPushButton('Save')
        save.clicked.connect(self.accept)
        form.addRow(save)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = Settings.load()
        self.messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        self.thread = None
        self.screenshot = None
        self.setWindowTitle('Local AI Assistant · Alpha')
        self.resize(420, 570)
        self.apply_flags()
        self.setStyleSheet("""
          QWidget {background:#141821; color:#e9edf5; font-size:13px;}
          QTextEdit,QPlainTextEdit,QLineEdit {background:#202735; border:1px solid #364052;
             border-radius:9px; padding:9px; selection-background-color:#3c6cc9;}
          QPushButton {background:#29354b; border:0; border-radius:9px; padding:10px;}
          QPushButton:hover {background:#364969;}
          QPushButton:checked {background:#245c49; border:1px solid #72d6a7;}
          QPushButton:disabled {color:#7f8899; background:#222936;}
        """)
        root = QVBoxLayout(self)
        root.setSpacing(10)
        top = QHBoxLayout()
        title = QLabel('◉  LOCAL AI ASSISTANT')
        title.setStyleSheet('font-weight:700; font-size:15px; color:#a9c6ff;')
        top.addWidget(title)
        top.addStretch()
        settings_button = QPushButton('⚙')
        settings_button.setToolTip('Settings')
        settings_button.clicked.connect(self.open_settings)
        top.addWidget(settings_button)
        root.addLayout(top)
        self.status = QLabel('Local · Advisor mode · No screen captured')
        self.status.setWordWrap(True)
        self.status.setStyleSheet('color:#a1acbd;')
        root.addWidget(self.status)
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setPlaceholderText('Ask about a problem or attach a screenshot…')
        root.addWidget(self.history, 1)
        self.input = QPlainTextEdit()
        self.input.setPlaceholderText('Write a question…')
        self.input.setFixedHeight(86)
        root.addWidget(self.input)
        bottom = QHBoxLayout()
        self.capture_button = QPushButton('◫  Capture screen')
        self.capture_button.setCheckable(True)
        self.update_capture_button()
        self.capture_button.clicked.connect(self.capture)
        bottom.addWidget(self.capture_button)
        clear = QPushButton('Clear')
        clear.clicked.connect(self.clear_chat)
        bottom.addWidget(clear)
        self.send_button = QPushButton('Send ↗')
        self.send_button.clicked.connect(self.send)
        bottom.addWidget(self.send_button)
        root.addLayout(bottom)
        hint = QLabel('Single screenshot per message · No live screen access')
        hint.setStyleSheet('color:#8290a5; font-size:11px;')
        root.addWidget(hint)

    def apply_flags(self):
        flags = Qt.WindowType.Window
        if self.settings.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                local_endpoint(dialog.endpoint.text().strip())
            except ValueError as exc:
                QMessageBox.warning(self, 'Invalid endpoint', str(exc))
                return
            self.settings.model = dialog.model.text().strip()
            self.settings.endpoint = dialog.endpoint.text().strip()
            self.settings.always_on_top = dialog.on_top.isChecked()
            self.settings.save()
            self.apply_flags()
            self.show()

    def update_capture_button(self):
        attached = self.screenshot is not None
        self.capture_button.setChecked(attached)
        self.capture_button.setText('✓  Remove screenshot' if attached else '◫  Capture screen')
        self.capture_button.setToolTip(
            'One screenshot is attached to the next message. Click to remove it.' if attached else
            'Take one screenshot for your next message. This does not enable live screen access.')

    def capture(self):
        if self.screenshot is not None:
            self.screenshot = None
            self.update_capture_button()
            self.status.setText('Screenshot removed · No screenshot attached')
            return
        try:
            self.screenshot = capture_primary_screen()
            self.status.setText('1 screenshot attached to next message · No live access')
        except Exception as exc:
            QMessageBox.warning(self, 'Capture failed', str(exc))
        self.update_capture_button()

    def clear_chat(self):
        if self.thread is not None:
            return
        self.messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        self.screenshot = None
        self.update_capture_button()
        self.history.clear()
        self.status.setText('Local · Advisor mode · No screen captured')

    def send(self):
        if self.thread is not None:
            return
        content = self.input.toPlainText().strip()
        if not content:
            if self.screenshot:
                content = 'Please describe and analyze this screenshot.'
            else:
                return
        self.input.clear()
        self.history.append(f'You: {content}\n')
        self.messages.append({'role': 'user', 'content': content})
        self.send_button.setEnabled(False)
        self.capture_button.setEnabled(False)
        self.status.setText('Thinking locally…')
        self.thread = QThread(self)
        self.worker = Worker(self.settings.endpoint, self.settings.model,
                             list(self.messages), self.screenshot)
        self.screenshot = None
        self.update_capture_button()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.success)
        self.worker.failed.connect(self.failure)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup)
        self.thread.start()

    @Slot(str)
    def success(self, answer):
        self.messages.append({'role': 'assistant', 'content': answer})
        self.history.append(f'Assistant: {answer}\n')
        self.status.setText('Local · Advisor mode · Ready')

    @Slot(str)
    def failure(self, message):
        self.messages.pop()
        self.history.append(f'Connection error: {message}\n')
        self.status.setText('Error · Check Ollama and selected model')

    @Slot()
    def cleanup(self):
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.thread = None
        self.send_button.setEnabled(True)
        self.capture_button.setEnabled(True)

    def closeEvent(self, event):
        if self.thread is not None:
            event.ignore()
            self.hide()
        else:
            super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Local AI Assistant')
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
