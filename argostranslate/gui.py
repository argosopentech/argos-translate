from pathlib import Path
import os
from functools import partial
from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from argostranslate import translate, package, settings, utils
from argostranslate.utils import info, error


class TranslationThread(QThread):
    send_text_update = pyqtSignal(str)

    def __init__(self, translation_function, show_loading_message):
        super().__init__()
        self.translation_function = translation_function
        self.show_loading_message = show_loading_message

    def run(self):
        if self.show_loading_message:
            self.send_text_update.emit("Loading...")
        translated_text = self.translation_function()
        self.send_text_update.emit(translated_text)


class WorkerStatusButton(QPushButton):
    class Status(Enum):
        NOT_STARTED = 0
        RUNNING = 1
        DONE = 2

    def __init__(self, text, bound_worker_function):
        super().__init__(text)
        self.text = text
        self.bound_worker_function = bound_worker_function
        self.clicked.connect(self.clicked_handler)
        self.set_status(self.Status.NOT_STARTED)

    def clicked_handler(self):
        info("WorkerStatusButton clicked_handler")
        if self.status == self.Status.NOT_STARTED:
            self.worker_thread = utils.WorkerThread(self.bound_worker_function)
            self.worker_thread.finished.connect(self.finished_handler)
            self.set_status(self.Status.RUNNING)
            self.worker_thread.start()

    def finished_handler(self):
        info("WorkerStatusButton finished_handler")
        self.set_status(self.Status.DONE)

    def set_status(self, status):
        self.status = status
        if self.status == self.Status.NOT_STARTED:
            self.setText(self.text)
        elif self.status == self.Status.RUNNING:
            self.setText("⌛")
        elif self.status == self.Status.DONE:
            self.setText("✓")


class PackagesTable(QTableWidget):
    packages_changed = pyqtSignal()

    class TableContent(Enum):
        INSTALLED = 0
        AVAILABLE = 1

    class AvailableActions(Enum):
        UNINSTALL = 0
        INSTALL = 1

    def __init__(self, table_content, available_actions):
        super().__init__()
        self.table_content = table_content
        self.available_actions = available_actions

        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        headers = ["Readme", "Name", "Package name", "From code", "To code", "Version"]
        if self.AvailableActions.UNINSTALL in self.available_actions:
            headers.append("Uninstall")
        if self.AvailableActions.INSTALL in self.available_actions:
            headers.append("Install")
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # Padding in header sections used as workaround for inaccurate results of resizeColumnsToContents()
        self.STRETCH_COLUMN_MIN_PADDING = 50
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        self.installed_packages = package.get_installed_packages()

    def get_packages(self):
        if self.table_content == self.TableContent.AVAILABLE:
            packages = package.get_available_packages()
        elif self.table_content == self.TableContent.INSTALLED:
            packages = package.get_installed_packages()
        else:
            raise Exception("Invalid table content")

        # Filter sbd packages in GUI
        packages = list(filter(lambda x: x.type != "sbd", packages))

        return packages

    def populate(self):
        packages = self.get_packages()

        self.setRowCount(len(packages))
        for i, pkg in enumerate(packages):
            name = str(pkg)
            package_name = package.argospm_package_name(pkg)
            package_version = pkg.package_version
            from_code = pkg.from_code
            to_code = pkg.to_code
            pkg = packages[i]
            readme_button = QPushButton("view")
            bound_view_package_readme_function = partial(self.view_package_readme, pkg)
            readme_button.clicked.connect(bound_view_package_readme_function)
            row_index = 0
            self.setCellWidget(i, row_index, readme_button)
            row_index += 1
            self.setItem(i, row_index, QTableWidgetItem(name))
            row_index += 1
            self.setItem(i, row_index, QTableWidgetItem(package_name))
            row_index += 1
            self.setItem(i, row_index, QTableWidgetItem(from_code))
            row_index += 1
            self.setItem(i, row_index, QTableWidgetItem(to_code))
            row_index += 1
            self.setItem(i, row_index, QTableWidgetItem(package_version))
            row_index += 1
            if self.AvailableActions.UNINSTALL in self.available_actions:
                uninstall_button = QPushButton("🗑")
                bound_uninstall_function = partial(
                    PackagesTable.uninstall_package, self, pkg
                )
                uninstall_button.clicked.connect(bound_uninstall_function)
                self.setCellWidget(i, row_index, uninstall_button)
                row_index += 1
            if self.AvailableActions.INSTALL in self.available_actions:
                if pkg not in self.installed_packages:
                    bound_install_function = partial(
                        PackagesTable.install_package, self, pkg
                    )
                    install_button = WorkerStatusButton("⬇", bound_install_function)
                    self.setCellWidget(i, row_index, install_button)
                else:
                    self.setItem(i, row_index, QTableWidgetItem("Installed"))
                row_index += 1
        # Resize table widget
        self.setMinimumSize(QSize(0, 0))
        self.resizeColumnsToContents()
        self.adjustSize()
        # Set minimum width of packages_table that also limits size of packages window
        header_width = self.horizontalHeader().length()
        self.setMinimumSize(
            QSize(header_width + self.STRETCH_COLUMN_MIN_PADDING * 2, 0)
        )

    def uninstall_package(self, pkg):
        try:
            package.uninstall(pkg)
        except OSError as e:
            # packages included in a snap archive are on a
            # read-only filesystem and can't be deleted
            if "SNAP" in os.environ:
                error_message_box = QMessageBox()
                error_message_box.setWindowTitle("Error")
                error_message_box.setText(
                    "Error deleting package: \n"
                    + "Packages pre-installed in a snap archive can't be deleted"
                )
                error_message_box.setIcon(QMessageBox.Warning)
                error_message_box.exec_()
            else:
                raise e
        self.packages_changed.emit()
        self.populate()
        self.packages_changed.emit()

    def install_package(self, pkg):
        download_path = pkg.download()
        package.install_from_path(download_path)
        os.remove(download_path)
        self.packages_changed.emit()

    def view_package_readme(self, pkg):
        about_message_box = QMessageBox()
        about_message_box.setWindowTitle(str(pkg))
        about_message_box.setText(pkg.get_description())
        about_message_box.setIcon(QMessageBox.Information)
        about_message_box.exec_()


class ManagePackagesWindow(QWidget):
    packages_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.packages_table = PackagesTable(
            PackagesTable.TableContent.INSTALLED,
            [PackagesTable.AvailableActions.UNINSTALL],
        )

        # Download packages
        def open_download_packages_view(self):
            self.download_packages_window = DownloadPackagesWindow()
            self.download_packages_window.packages_changed.connect(
                partial(PackagesTable.populate, self.packages_table)
            )
            self.download_packages_window.show()
            self.download_packages_window.packages_changed.connect(
                self.packages_changed.emit
            )

        self.download_packages_button = QPushButton("Download packages")
        self.download_packages_button.clicked.connect(
            partial(open_download_packages_view, self)
        )

        # Install from file
        self.install_package_file_button = QPushButton("Install package file")
        self.install_package_file_button.clicked.connect(self.add_packages)

        # Add packages row
        self.add_packages_row_layout = QHBoxLayout()
        self.add_packages_row_layout.addWidget(self.download_packages_button)
        self.add_packages_row_layout.addWidget(self.install_package_file_button)
        self.add_packages_row_layout.addStretch()

        # Packages table
        self.packages_table.packages_changed.connect(self.packages_changed.emit)
        self.packages_table.populate()
        self.packages_layout = QVBoxLayout()
        self.packages_layout.addWidget(self.packages_table)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.add_packages_row_layout)
        self.layout.addLayout(self.packages_layout)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def add_packages(self):
        file_dialog = QFileDialog()
        filepaths = file_dialog.getOpenFileNames(
            self,
            "Select .argosmodel package files",
            str(Path.home()),
            "Argos Models (*.argosmodel)",
        )[0]
        if len(filepaths) > 0:
            for file_path in filepaths:
                package.install_from_path(file_path)
            self.packages_changed.emit()
            self.packages_table.populate()


class DownloadPackagesWindow(QWidget):
    packages_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Update package definitions from remote
        package.update_package_index()

        # Load available packages from local package index
        available_packages = package.get_available_packages()

        # Packages table
        self.packages_table = PackagesTable(
            PackagesTable.TableContent.AVAILABLE,
            [PackagesTable.AvailableActions.INSTALL],
        )
        self.packages_table.packages_changed.connect(self.packages_changed.emit)
        self.packages_table.populate()
        self.packages_layout = QVBoxLayout()
        self.packages_layout.addWidget(self.packages_table)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.packages_layout)
        self.layout.addStretch()
        self.setLayout(self.layout)


class GUIWindow(QMainWindow):
    # Above this number of characters in the input text will show a
    # message in the output text while the translation
    # is happening
    SHOW_LOADING_THRESHOLD = 300

    def __init__(self):
        super().__init__()

        # Threading
        self.worker_thread = None

        # This is an instance of TranslationThread to run after
        # the currently running TranslationThread finishes.
        # None if there is no waiting TranslationThread.
        self.queued_translation = None

        # Language selection
        self.left_language_combo = QComboBox()
        self.language_swap_button = QPushButton("↔")
        self.right_language_combo = QComboBox()
        self.left_language_combo.currentIndexChanged.connect(self.translate)
        self.right_language_combo.currentIndexChanged.connect(self.translate)
        self.language_swap_button.clicked.connect(self.swap_languages_button_clicked)
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
        self.left_textEdit.setPlainText("Text to translate from")
        self.left_textEdit.textChanged.connect(self.translate)
        self.right_textEdit = QTextEdit()
        self.right_textEdit.setPlainText("Text to translate to")
        self.textEdit_layout = QHBoxLayout()
        self.textEdit_layout.addWidget(self.left_textEdit)
        self.textEdit_layout.addWidget(self.right_textEdit)

        # Menu
        self.menu = self.menuBar()
        self.manage_packages_action = self.menu.addAction("Manage Packages")
        self.manage_packages_action.triggered.connect(
            self.manage_packages_action_triggered
        )
        self.about_action = self.menu.addAction("About")
        self.about_action.triggered.connect(self.about_action_triggered)
        self.menu.setNativeMenuBar(False)

        # Load languages
        self.load_languages()

        # Final setup
        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(self.language_selection_layout)
        self.window_layout.addLayout(self.textEdit_layout)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.window_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Argos Translate")

    def swap_languages_button_clicked(self):
        left_index = self.left_language_combo.currentIndex()
        self.left_language_combo.setCurrentIndex(
            self.right_language_combo.currentIndex()
        )
        self.right_language_combo.setCurrentIndex(left_index)

    def about_action_triggered(self):
        about_message_box = QMessageBox()
        about_message_box.setWindowTitle("About")
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
        if len(language_names) > 0:
            self.left_language_combo.setCurrentIndex(0)
        self.right_language_combo.clear()
        self.right_language_combo.addItems(language_names)
        if len(language_names) > 1:
            self.right_language_combo.setCurrentIndex(1)
        self.translate()

    def update_right_textEdit(self, text):
        self.right_textEdit.setPlainText(text)

    def handle_worker_thread_finished(self):
        self.worker_thread = None
        if self.queued_translation is not None:
            self.worker_thread = self.queued_translation
            self.worker_thread.start()
            self.queued_translation = None

    def translate(self):
        """Try to translate based on languages selected."""
        if len(self.languages) < 1:
            return
        input_text = self.left_textEdit.toPlainText()
        input_combo_value = self.left_language_combo.currentIndex()
        input_language = self.languages[input_combo_value]
        output_combo_value = self.right_language_combo.currentIndex()
        output_language = self.languages[output_combo_value]
        translation = input_language.get_translation(output_language)
        if translation:
            bound_translation_function = partial(translation.translate, input_text)
            show_loading_message = len(input_text) > self.SHOW_LOADING_THRESHOLD
            new_worker_thread = TranslationThread(
                bound_translation_function, show_loading_message
            )
            new_worker_thread.send_text_update.connect(self.update_right_textEdit)
            new_worker_thread.finished.connect(self.handle_worker_thread_finished)
            if self.worker_thread is None:
                self.worker_thread = new_worker_thread
                self.worker_thread.start()
            else:
                self.queued_translation = new_worker_thread

        else:
            error("No translation available for this language pair")


class GUIApplication:
    def __init__(self):
        self.app = QApplication([])
        self.main_window = GUIWindow()

        # Icon
        icon_path = Path(os.path.dirname(__file__)) / "img" / "icon.png"
        icon_path = str(icon_path)
        self.app.setWindowIcon(QIcon(icon_path))

        self.main_window.show()
        self.app.exec_()


def main():
    app = GUIApplication()
