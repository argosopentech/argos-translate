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

class ManagePackagesWindow(QWidget):
    packages_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Add packages row
        self.add_packages_button = QPushButton('+ Add packages')
        self.add_packages_button.clicked.connect(self.add_packages)
        self.add_packages_row_layout = QHBoxLayout()
        self.add_packages_row_layout.addWidget(
                self.add_packages_button)
        self.add_packages_row_layout.addStretch()

        # Packages table
        self.packages_table = QTableWidget()
        self.packages_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.packages_table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.packages_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.packages_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.packages_table.setColumnCount(8)
        self.packages_table.setHorizontalHeaderLabels([
                'Readme',
                'From name',
                'To name',
                'Package version',
                'Argos version',
                'From code',
                'To code',
                'Uninstall'
            ])
        self.packages_table.verticalHeader().setVisible(False)
        self.packages_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.packages_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.packages_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # Padding in header sections used as workaround for inaccurate results of resizeColumnsToContents()
        self.packages_table.STRETCH_COLUMN_MIN_PADDING = 50
        self.packages_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.populate_packages_table()
        self.packages_layout = QVBoxLayout()
        self.packages_layout.addWidget(self.packages_table)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.add_packages_row_layout)
        self.layout.addLayout(self.packages_layout)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def uninstall_package(self, pkg):
        try:
            package.uninstall(pkg)
        except OSError as e:
            # packages included in a snap archive are on a
            # read-only filesystem and can't be deleted
            if 'SNAP' in os.environ:
                about_message_box = QMessageBox()
                about_message_box.setWindowTitle('Error')
                about_message_box.setText('Error deleting package: \n' + 
                    'Packages pre-installed in a snap archive can\'t be deleted')
                about_message_box.setIcon(QMessageBox.Warning)
                about_message_box.exec_()
            else:
                raise e
        self.populate_packages_table()
        self.packages_changed.emit()

    def view_package_readme(self, pkg):
        about_message_box = QMessageBox()
        about_message_box.setWindowTitle(str(pkg))
        about_message_box.setText(pkg.get_readme())
        about_message_box.setIcon(QMessageBox.Information)
        about_message_box.exec_()

    def add_packages(self):
        file_dialog = QFileDialog()
        filepaths = file_dialog.getOpenFileNames(
                self,
                'Select .argosmodel package files',
                str(Path.home()),
                'Argos Models (*.argosmodel)')[0]
        if len(filepaths) > 0:
            for file_path in filepaths:
                package.install_from_path(file_path)
            self.populate_packages_table()
            self.packages_changed.emit()

    def populate_packages_table(self):
        packages = package.get_installed_packages()
        self.packages_table.setRowCount(len(packages))
        for i, pkg in enumerate(packages):
            from_name = pkg.from_name
            to_name = pkg.to_name
            package_version = pkg.package_version
            argos_version = pkg.argos_version
            from_code = pkg.from_code
            to_code = pkg.to_code
            pkg = packages[i]
            readme_button = QPushButton('view')
            bound_view_package_readme_function = functools.partial(
                self.view_package_readme, pkg)
            readme_button.clicked.connect(bound_view_package_readme_function)
            self.packages_table.setCellWidget(i, 0, readme_button)
            self.packages_table.setItem(i, 1, QTableWidgetItem(from_name))
            self.packages_table.setItem(i, 2, QTableWidgetItem(to_name))
            self.packages_table.setItem(i, 3, QTableWidgetItem(package_version))
            self.packages_table.setItem(i, 4, QTableWidgetItem(argos_version))
            self.packages_table.setItem(i, 5, QTableWidgetItem(from_code))
            self.packages_table.setItem(i, 6, QTableWidgetItem(to_code))
            delete_button = QPushButton('x')
            bound_delete_function = functools.partial(self.uninstall_package, pkg)
            delete_button.clicked.connect(bound_delete_function)
            self.packages_table.setCellWidget(i, 7, delete_button)
        # Resize table widget
        self.packages_table.setMinimumSize(QSize(0, 0))
        self.packages_table.resizeColumnsToContents()
        self.packages_table.adjustSize()
        # Set minimum width of packages_table that also limits size of packages window
        header_width = self.packages_table.horizontalHeader().length()
        self.packages_table.setMinimumSize(
            QSize(header_width + self.packages_table.STRETCH_COLUMN_MIN_PADDING * 2, 0)
        )

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
        self.manage_packages_action = self.menu.addAction('Manage Packages')
        self.manage_packages_action.triggered.connect(
                self.manage_packages_action_triggered)
        self.about_action = self.menu.addAction('About')
        self.about_action.triggered.connect(self.about_action_triggered)

        # Icon
        icon_path = Path(os.path.dirname(__file__)) / 'img' / 'icon.png'
        icon_path = str(icon_path)
        self.setWindowIcon(QIcon(icon_path))

        # Load languages
        self.load_languages()

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

    def manage_packages_action_triggered(self):
        self.packages_window = ManagePackagesWindow()
        self.packages_window.packages_changed.connect(self.load_languages)
        self.packages_window.show()

    def load_languages(self):
        self.languages = translate.load_installed_languages()
        language_names = tuple([language.name for language in self.languages])
        self.left_language_combo.clear()
        self.left_language_combo.addItems(language_names)
        if len(language_names) > 0: self.left_language_combo.setCurrentIndex(0)
        self.right_language_combo.clear()
        self.right_language_combo.addItems(language_names)
        if len(language_names) > 1: self.right_language_combo.setCurrentIndex(1)
        self.translate()

    def update_right_textEdit(self, text):
        self.right_textEdit.setPlainText(text)

    def handle_worker_thread_finished(self):
        self.worker_thread = None
        if self.queued_translation != None:
            self.worker_thread = self.queued_translation
            self.worker_thread.start()
            self.queued_translation = None

    def translate(self):
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
            print('No translation available for this language pair')

class GUIApplication:
    def __init__(self):
        self.app = QApplication([])
        self.main_window = GUIWindow()
        self.main_window.show()
        self.app.exec_()

def main():
    app = GUIApplication()

