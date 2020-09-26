from pathlib import Path
import os
import threading
import functools

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from argostranslate import translate, package, settings

class WorkerThread(QThread):
    send_text_update = pyqtSignal(str)

    def __init__(self, translation_function, show_loading_message):
        super().__init__()
        self.translation_function = translation_function
        self.show_loading_message = show_loading_message

    def __del__(self):
        self.wait()

    def run(self):
        if self.show_loading_message:
            self.send_text_update.emit('Loading...')
        translated_text = self.translation_function()
        self.send_text_update.emit(translated_text)

class GUIWindow(QMainWindow):
    # Above this number of characters in the input text will show a 
    # message in the output text while the translation
    # is happening
    SHOW_LOADING_THRESHOLD = 300

    def __init__(self):
        super().__init__()

        # Threading
        self.worker_thread = None

        # This is an instance of WorkerThread to run after
        # the currently running WorkerThread finishes.
        # None if there is no waiting WorkerThread.
        self.queued_translation = None

        # Language selection
        self.left_language_combo = QComboBox()
        self.language_swap_button = QPushButton('↔')
        self.right_language_combo = QComboBox()
        self.left_language_combo.currentIndexChanged.connect(
                self.translate)
        self.right_language_combo.currentIndexChanged.connect(
                self.translate)
        self.language_swap_button.clicked.connect(
                self.swap_languages_button_clicked)
        self.language_selection_layout = QHBoxLayout()
        self.language_selection_layout.addStretch()
        self.language_selection_layout.addWidget(self.left_language_combo)
        self.language_selection_layout.addStretch()
        self.language_selection_layout.addWidget(self.language_swap_button)
        self.language_selection_layout.addStretch()
        self.language_selection_layout.addWidget(self.right_language_combo)
        self.language_selection_layout.addStretch()

        # TextEdits
        self.left_textEdit = QTextEdit()
        self.left_textEdit.setPlainText('Text to translate from')
        self.left_textEdit.textChanged.connect(self.translate)
        self.right_textEdit = QTextEdit()
        self.right_textEdit.setPlainText('Text to translate to')
        self.textEdit_layout = QHBoxLayout()
        self.textEdit_layout.addWidget(self.left_textEdit)
        self.textEdit_layout.addWidget(self.right_textEdit)

        # Menu
        self.menu = self.menuBar()
        self.about_action = self.menu.addAction('About')
        self.about_action.triggered.connect(self.about_action_triggered)

        # Load languages
        self.load_languages()

        # Translate demo text
        self.translate()

        # Final setup
        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(self.language_selection_layout)
        self.window_layout.addLayout(self.textEdit_layout)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.window_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle('Argos Translate')

    def swap_languages_button_clicked(self):
        left_index = self.left_language_combo.currentIndex()
        self.left_language_combo.setCurrentIndex(
                self.right_language_combo.currentIndex())
        self.right_language_combo.setCurrentIndex(left_index)

    def about_action_triggered(self):
        about_message_box = QMessageBox()
        about_message_box.setWindowTitle('About')
        about_message_box.setText(settings.about_text)
        about_message_box.setIcon(QMessageBox.Information)
        about_message_box.exec_()

    def load_languages(self):
        self.languages = translate.load_installed_languages()
        language_names = tuple([language.name for language in self.languages])
        self.left_language_combo.addItems(language_names)
        if len(language_names) > 0: self.left_language_combo.setCurrentIndex(0)
        self.right_language_combo.addItems(language_names)
        if len(language_names) > 1: self.right_language_combo.setCurrentIndex(1)

    def update_right_textEdit(self, text):
        self.right_textEdit.setPlainText(text)

    def handle_worker_thread_finished(self):
        self.worker_thread = None
        if self.queued_translation != None:
            self.worker_thread = self.queued_translation
            self.worker_thread.start()
            self.queued_translation = None

    def translate(self, showError=True):
        """Try to translate based on languages selected.

        Args:
            showError (bool): If True show an error messagebox if the
                currently selected translation isn't installed
        """
        if len(self.languages) < 1: return
        input_text = self.left_textEdit.toPlainText()
        input_combo_value = self.left_language_combo.currentIndex()
        input_language = self.languages[input_combo_value]
        output_combo_value = self.right_language_combo.currentIndex()
        output_language = self.languages[output_combo_value]
        translation = input_language.get_translation(output_language)
        if translation:
            bound_translation_function = functools.partial(translation.translate,
                    input_text)
            show_loading_message = len(input_text) > self.SHOW_LOADING_THRESHOLD
            new_worker_thread = WorkerThread(bound_translation_function,
                    show_loading_message)
            new_worker_thread.send_text_update.connect(
                    self.update_right_textEdit)
            new_worker_thread.finished.connect(
                    self.handle_worker_thread_finished)
            if self.worker_thread == None:
                self.worker_thread = new_worker_thread
                self.worker_thread.start()
            else:
                self.queued_translation = new_worker_thread

        else:
            if showError:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Warning)
                error_dialog.setText('No translation installed between these languages')
                error_dialog.setWindowTitle('Error')
                error_dialog.exec_()

app = QApplication([])
main_window = GUIWindow()
main_window.show()
app.exec_()
