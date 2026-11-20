import sys
from pathlib import Path
from copy import deepcopy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from threading import Event

from PySide6.QtCore import (
    Qt,
    QObject,
    QThread,
    Signal
)

from PySide6.QtCore import (
    Qt,
    QObject,
    QThread,
    Signal,
    QUrl,
)

from PySide6.QtGui import QDesktopServices

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QProgressBar,
    QDialog,
    QListWidget,
    QDialogButtonBox,
    QInputDialog,
    QMessageBox,
)


from organizer import analyze_folder, organize_files
from file_stats import format_size
from settings import load_settings, save_settings
from default_rules import DEFAULT_RULES

class OrganizeWorker(QObject):

    progress = Signal(int)

    finished = Signal(
        object,
        object
    )

    cancelled = Signal()

    error = Signal(str)

    def __init__(
        self,
        folder,
        rules
    ):
        super().__init__()

        self.folder = folder
        self.rules = deepcopy(rules)

        self.cancel_event = Event()

    def run(self):
        try:
            stats, output_root = organize_files(
                self.folder,
                self.rules,
                progress_callback=self.progress.emit,
                cancel_check=self.cancel_event.is_set
            )

            if self.cancel_event.is_set():
                self.cancelled.emit()

            else:
                self.finished.emit(
                    stats,
                    output_root
                )

        except Exception as e:
            self.error.emit(
                str(e)
            )

    def cancel(self):
        self.cancel_event.set()

class FileInsightWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_folder = None
        self.output_folder = None
        self.thread = None
        self.worker = None
        self.close_pending = False

        self.settings = load_settings()

        self.rules = deepcopy(
            self.settings.get(
                "rules",
                DEFAULT_RULES
            )
        )

        self.path_label = QLabel(
            "No folder selected"
        )

        last_folder = self.settings.get(
            "last_folder",
            ""
        )

        if last_folder:
            folder = Path(
                last_folder
            )

            if folder.exists():
                self.selected_folder = folder

                self.path_label.setText(
                    f"Folder: {self.selected_folder}"
                )

        self.setWindowTitle("FileInsight")

        window_width = self.settings.get(
            "window_width",
            1100
        )

        window_height = self.settings.get(
            "window_height",
            750
        )

        window_x = self.settings.get(
            "window_x",
            100
        )

        window_y = self.settings.get(
            "window_y",
            100
        )

        self.resize(
            window_width,
            window_height
        )

        self.move(
            window_x,
            window_y
        )

        self.m_layout = QVBoxLayout()

        self.m_layout.setContentsMargins(
            24,
            24,
            24,
            24
        )

        self.m_layout.setSpacing(
            14
        )

        self.title_label = QLabel(
            "FileInsight"
        )


        self.status_label = QLabel(
            "Status: Ready"
        )

        self.empty_label = QLabel(
            "Select a folder and click Analyze"
        )

        self.title_label.setAlignment(
            Qt.AlignCenter
        )

        self.empty_label.setAlignment(
            Qt.AlignCenter
        )

        self.title_label.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            """
        )

        self.empty_label.setStyleSheet(
            """
            font-size: 18px;
            color: gray;
            """
        )

        self.browse_button = QPushButton(
            "Browse"
        )

        self.analyze_button = QPushButton(
            "Analyze"
        )

        self.organize_button = QPushButton(
            "Organize Files"
        )

        self.rules_button = QPushButton(
            "Edit Rules"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setEnabled(
            False
        )

        has_folder = self.selected_folder is not None

        self.analyze_button.setEnabled(
            has_folder
        )

        self.organize_button.setEnabled(
            has_folder
        )

        #region Progress Bar
        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_bar.setVisible(
            False
        )
        #endregion

        #region Layouts
        self.button_layout = QHBoxLayout()

        self.button_layout.setSpacing(
            10
        )

        self.button_layout.addWidget(
            self.analyze_button
        )

        self.button_layout.addWidget(
            self.organize_button
        )

        self.button_layout.addWidget(
            self.rules_button
        )

        self.button_layout.addWidget(
            self.cancel_button
        )

        self.stats_table = QTableWidget()

        self.setup_table()

        self.bar_figure = Figure()

        self.bar_canvas = FigureCanvas(
            self.bar_figure
        )

        self.pie_figure = Figure()

        self.pie_canvas = FigureCanvas(
            self.pie_figure
        )

        self.chart_layout = QHBoxLayout()

        self.chart_layout.setSpacing(
            12
        )

        self.chart_layout.addWidget(
            self.bar_canvas
        )

        self.chart_layout.addWidget(
            self.pie_canvas
        )

        self.stats_table.setVisible(
            False
        )

        self.bar_canvas.setVisible(
            False
        )

        self.pie_canvas.setVisible(
            False
        )

        self.m_layout.addWidget(
            self.title_label
        )

        self.m_layout.addWidget(
            self.path_label
        )

        self.m_layout.addWidget(
            self.browse_button
        )

        self.m_layout.addLayout(
            self.button_layout
        )

        self.m_layout.addWidget(
            self.progress_bar
        )

        self.m_layout.addWidget(
            self.empty_label
        )

        self.m_layout.addWidget(
            self.stats_table
        )

        self.m_layout.addLayout(
            self.chart_layout
        )

        self.open_output_button = QPushButton(
            "Open Output Folder"
        )

        self.open_output_button.setEnabled(False)

        self.open_output_button.clicked.connect(
            self.open_output_folder
        )

        self.status_layout = QHBoxLayout()

        self.status_layout.addWidget(
            self.status_label
        )

        self.status_layout.addStretch()

        self.status_layout.addWidget(
            self.open_output_button
        )

        self.m_layout.addLayout(
            self.status_layout
        )

        self.setLayout(
            self.m_layout
        )
        #endregion

        #region Connections
        self.browse_button.clicked.connect(
            self.select_folder
        )

        self.analyze_button.clicked.connect(
            self.analyze_selected_folder
        )

        self.organize_button.clicked.connect(
            self.organize_selected_folder
        )

        self.rules_button.clicked.connect(
            self.open_rules_editor
        )

        self.cancel_button.clicked.connect(
            self.cancel_organize
        )
        #endregion

    def closeEvent(self, event):
        if self.thread is not None:
            # Keep the window alive until thread cleanup finishes.
            event.ignore()

            if self.close_pending:
                return

            answer = QMessageBox.question(
                self,
                "Cancel and Exit",
                "Cancel organizing and exit?\n"
                "Files already copied will be kept.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:
                return

            self.close_pending = True
            self.setEnabled(False)

            self.status_label.setText(
                "Status: Waiting for the task to finish before closing..."
            )

            # The task may have finished while the prompt was open.
            if self.thread is None:
                self.close()
                return

            if self.worker is not None:
                self.worker.cancel_event.set()

            return

        self.settings["window_width"] = self.width()
        self.settings["window_height"] = self.height()
        self.settings["window_x"] = self.x()
        self.settings["window_y"] = self.y()

        try:
            save_settings(self.settings)
        except OSError as error:
            event.ignore()
            self.close_pending = False
            self.setEnabled(True)

            QMessageBox.warning(
                self,
                "Save Failed",
                str(error)
            )
            return

        event.accept()

    def setup_table(self):
        self.stats_table.setColumnCount(
            3
        )

        self.stats_table.setHorizontalHeaderLabels(
            [
                "Category",
                "Files",
                "Size"
            ]
        )

        self.stats_table.verticalHeader().setVisible(
            False
        )

        self.stats_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.stats_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.stats_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        header = self.stats_table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )

        if folder_path:
            self.selected_folder = Path(
                folder_path
            )

            self.settings["last_folder"] = folder_path

            save_settings(
                self.settings
            )

            self.path_label.setText(
                f"Folder: {self.selected_folder}"
            )

            self.analyze_button.setEnabled(
                True
            )

            self.organize_button.setEnabled(
                True
            )

            self.status_label.setText(
                "Status: Folder selected"
            )

            self.empty_label.setVisible(
                True
            )

            self.empty_label.setText(
                "Click Analyze to inspect this folder"
            )

            self.stats_table.setVisible(
                False
            )

            self.bar_canvas.setVisible(
                False
            )

            self.pie_canvas.setVisible(
                False
            )

    def open_rules_editor(self):
        # Prevent rule editing while organization is running.
        if self.thread is not None:
            return

        dialog = RulesEditor(
            self.rules,
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        # Prepare updated settings without changing the current settings.
        updated_settings = deepcopy(self.settings)
        updated_settings["rules"] = deepcopy(dialog.rules)

        try:
            save_settings(updated_settings)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Save Failed",
                str(error)
            )
            return

        # Apply the settings to the window after saving succeeds.
        self.settings = updated_settings
        self.rules = deepcopy(dialog.rules)

        # Hide statistics based on the old rules until the next analysis.
        self.stats_table.setVisible(False)
        self.bar_canvas.setVisible(False)
        self.pie_canvas.setVisible(False)

        self.empty_label.setVisible(True)
        self.empty_label.setText(
            "Rules saved. Click Analyze to refresh."
        )

        self.status_label.setText(
            "Status: Rules saved"
        )

    def analyze_selected_folder(self):
        if self.selected_folder is None:
            return

        self.status_label.setText(
            "Status: Analyzing..."
        )

        stats = analyze_folder(
            self.selected_folder,
            self.rules
            
        )

        self.update_stats_table(
            stats
        )

        self.update_charts(
            stats
        )

        self.show_statistics()

        self.status_label.setText(
            "Status: Analysis complete"
        )

    def organize_selected_folder(self):
        if self.selected_folder is None:
            return

        if self.thread is not None:
            return

        output_root = (
            self.selected_folder.parent
            / f"{self.selected_folder.name}_organized"
        )

        if output_root.exists():
            answer = QMessageBox.question(
                self,
                "Output Folder Already Exists",
                f"An output folder already exists:\n{output_root}\n\n"
                "Continue organizing into a new numbered folder?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:
                return
            
        self.status_label.setText(
            "Status: Organizing..."
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_bar.setVisible(
            True
        )

        self.cancel_button.setEnabled(
            True
        )

        self.organize_button.setEnabled(
            False
        )

        self.analyze_button.setEnabled(
            False
        )

        self.browse_button.setEnabled(
            False
        )

        self.thread = QThread()

        self.worker = OrganizeWorker(
            self.selected_folder,
            self.rules
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.progress.connect(
            self.progress_bar.setValue
        )

        self.worker.finished.connect(
            self.organize_finished
        )

        self.worker.cancelled.connect(
            self.organize_cancelled
        )

        self.worker.error.connect(
            self.organize_error
        )

        # Stop the thread when the task ends.
        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.cancelled.connect(
            self.thread.quit
        )

        self.worker.error.connect(
            self.thread.quit
        )

        # Clean up the worker.
        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.cancelled.connect(
            self.worker.deleteLater
        )

        self.worker.error.connect(
            self.worker.deleteLater
        )

        # Clean up the thread.
        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.organize_thread_finished
        )

        # Start the thread after all connections are configured.
        self.thread.start()

    def finish_organize_ui(self):
        self.progress_bar.setVisible(
            False
        )
        self.cancel_button.setEnabled(
            False
        )

        self.organize_button.setEnabled(
            True
        )

        self.analyze_button.setEnabled(
            True
        )

        self.browse_button.setEnabled(
            True
        )

    def organize_finished(
        self,
        stats,
        output_root
    ):
        self.output_folder = Path(output_root)

        self.open_output_button.setEnabled(
            self.output_folder.is_dir()
        )
        self.update_stats_table(
            stats
        )

        self.update_charts(
            stats
        )

        self.show_statistics()

        self.progress_bar.setValue(
            100
        )

        self.status_label.setText(
            f"Status: Done - {output_root}"
        )

        self.finish_organize_ui()

    def open_output_folder(self):
        if self.output_folder is None:
            return

        if not self.output_folder.is_dir():
            QMessageBox.warning(
                self,
                "Folder Not Found",
                "The output folder no longer exists."
            )
            self.open_output_button.setEnabled(False)
            return

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(self.output_folder.resolve())
            )
        )

        if not opened:
            QMessageBox.warning(
                self,
                "Open Failed",
                "Could not open the output folder."
            )

    def cancel_organize(self):
        if self.worker is None:
            return

        self.status_label.setText(
            "Status: Cancelling..."
        )

        self.cancel_button.setEnabled(
            False
        )

        self.worker.cancel()

    def organize_cancelled(self):
        self.status_label.setText(
            "Status: Cancelled"
        )

        self.finish_organize_ui()

    def organize_error(
        self,
        message
    ):
        self.status_label.setText(
            f"Status: Error - {message}"
        )

        self.finish_organize_ui()   

    def organize_thread_finished(self):
        self.thread = None
        self.worker = None

        if self.close_pending:
            self.close()

    def show_statistics(self):
        self.empty_label.setVisible(
            False
        )

        self.stats_table.setVisible(
            True
        )

        self.bar_canvas.setVisible(
            True
        )

        self.pie_canvas.setVisible(
            True
        )

    def update_stats_table(self, stats):
        self.stats_table.setRowCount(
            len(stats)
        )

        row = 0

        for category, data in stats.items():
            category_item = QTableWidgetItem(
                category
            )

            count_item = QTableWidgetItem(
                str(data["count"])
            )

            size_item = QTableWidgetItem(
                format_size(
                    data["size"]
                )
            )

            category_item.setTextAlignment(
                Qt.AlignCenter
            )

            count_item.setTextAlignment(
                Qt.AlignCenter
            )

            size_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.stats_table.setItem(
                row,
                0,
                category_item
            )

            self.stats_table.setItem(
                row,
                1,
                count_item
            )

            self.stats_table.setItem(
                row,
                2,
                size_item
            )

            row += 1

    def update_charts(self, stats):
        categories = []
        sizes_mb = []

        for category, data in stats.items():
            categories.append(
                category
            )

            sizes_mb.append(
                data["size"] / (1024 ** 2)
            )

        self.bar_figure.clear()

        bar_axes = self.bar_figure.add_subplot(
            111
        )

        bar_axes.bar(
            categories,
            sizes_mb
        )

        bar_axes.set_title(
            "File Size by Category"
        )

        bar_axes.set_xlabel(
            "Category"
        )

        bar_axes.set_ylabel(
            "Size (MB)"
        )

        self.bar_figure.tight_layout()

        self.bar_canvas.draw()

        pie_labels = []
        pie_sizes = []

        for category, data in stats.items():
            if data["size"] > 0:
                pie_labels.append(
                    category
                )

                pie_sizes.append(
                    data["size"]
                )

        self.pie_figure.clear()

        pie_axes = self.pie_figure.add_subplot(
            111
        )

        if pie_sizes:
            wedges, texts, autotexts = pie_axes.pie(
                pie_sizes,
                autopct="%1.1f%%",
                startangle=90
            )

            pie_axes.legend(
                wedges,
                pie_labels,
                title="Categories",
                loc="center left",
                bbox_to_anchor=(0.92, 0.5)
            )

        pie_axes.set_title(
            "Storage Distribution"
        )

        self.pie_figure.tight_layout()

        self.pie_canvas.draw()

class RulesEditor(QDialog):
    def __init__(self, rules, parent=None):
        super().__init__(parent)

        # Edit an independent copy of the main window rules.
        self.rules = deepcopy(rules)

        self.setWindowTitle("Rules Editor")
        self.resize(600, 400)

        self.category_list = QListWidget()
        self.extension_list = QListWidget()

        # Left column: categories.
        category_layout = QVBoxLayout()
        category_layout.addWidget(QLabel("Categories"))
        category_layout.addWidget(self.category_list)
        self.add_category_button = QPushButton(
            "Add Category"
        )

        category_layout.addWidget(
            self.add_category_button
        )

        self.add_category_button.clicked.connect(
            self.add_category
        )

        self.delete_category_button = QPushButton(
            "Delete Category"
        )

        category_layout.addWidget(
            self.delete_category_button
        )

        self.delete_category_button.clicked.connect(
            self.delete_category
        )

        self.rename_category_button = QPushButton(
            "Rename Category"
        )

        category_layout.addWidget(
            self.rename_category_button
        )

        self.rename_category_button.clicked.connect(
            self.rename_category
        )

        # Right column: extensions.
        extension_layout = QVBoxLayout()
        extension_layout.addWidget(QLabel("Extensions"))
        extension_layout.addWidget(self.extension_list)
        self.add_extension_button = QPushButton(
            "Add Extension"
        )

        extension_layout.addWidget(
            self.add_extension_button
        )

        self.add_extension_button.clicked.connect(
            self.add_extension
        )

        self.delete_extension_button = QPushButton(
            "Delete Extension"
        )

        extension_layout.addWidget(
            self.delete_extension_button
        )

        self.rename_extension_button = QPushButton(
            "Rename Extension"
        )

        extension_layout.addWidget(
            self.rename_extension_button
        )

        self.rename_extension_button.clicked.connect(
            self.rename_extension
        )

        self.delete_extension_button.clicked.connect(
            self.delete_extension
        )


        columns_layout = QHBoxLayout()
        columns_layout.addLayout(category_layout)
        columns_layout.addLayout(extension_layout)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.reset_rules_button = QPushButton(
            "Reset Default"
        )

        self.reset_rules_button.clicked.connect(
            self.reset_rules
        )

        # Bottom row: reset on the left, Save and Cancel on the right.
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.reset_rules_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.buttons)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(columns_layout)
        main_layout.addLayout(bottom_layout)

        # Update the extension list when the selected category changes.
        self.category_list.currentTextChanged.connect(
            self.show_extensions
        )

        self.category_list.addItems(
            list(self.rules.keys())
        )

        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

    def show_extensions(self, category):
        self.extension_list.clear()

        self.extension_list.addItems(
            self.rules.get(category, [])
        )

    def validate_category_name(self, name, original_name=None):
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Category",
                "Category name cannot be empty."
            )
            return False

        reserved_names = {
            "OTHERS", "CON", "PRN", "AUX", "NUL"
        }

        reserved_names.update(
            f"{prefix}{number}"
            for prefix in ("COM", "LPT")
            for number in range(1, 10)
        )

        invalid_characters = '<>:"/\\|?*'

        if (
            name.endswith(".")
            or any(char in invalid_characters for char in name)
            or any(ord(char) < 32 for char in name)
            or name.split(".")[0].upper() in reserved_names
        ):
            QMessageBox.warning(
                self,
                "Invalid Category",
                "Use a valid folder name. OTHERS is reserved."
            )
            return False

        if any(
            existing != original_name
            and existing.casefold() == name.casefold()
            for existing in self.rules
        ):
            QMessageBox.warning(
                self,
                "Duplicate Category",
                "This category already exists."
            )
            return False

        return True

    def validate_extension(self, extension):
        invalid_characters = '<>:"/\\|?*.'

        if (
            not extension.startswith(".")
            or len(extension) < 2
            or any(
                char in invalid_characters
                or char.isspace()
                or ord(char) < 32
                for char in extension[1:]
            )
        ):
            QMessageBox.warning(
                self,
                "Invalid Extension",
                "Use a single extension such as .blend."
            )
            return False

        for category, extensions in self.rules.items():
            if extension in extensions:
                QMessageBox.warning(
                    self,
                    "Duplicate Extension",
                    f"{extension} already belongs to {category}."
                )
                return False

        return True

    def add_category(self):
        name, accepted = QInputDialog.getText(
            self,
            "Add Category",
            "Category name:"
        )

        if not accepted:
            return

        name = name.strip()

        if not self.validate_category_name(name):
            return

        self.rules[name] = []
        self.category_list.addItem(name)

        self.category_list.setCurrentRow(
            self.category_list.count() - 1
        )

    def delete_category(self):
        item = self.category_list.currentItem()

        if item is None:
            return

        category = item.text()

        # Remove the category and its extensions from the rules copy.
        del self.rules[category]

        # Remove the corresponding row from the list.
        row = self.category_list.row(item)
        self.category_list.takeItem(row)

        # Refresh extensions, including when the last category is removed.
        current_item = self.category_list.currentItem()

        self.show_extensions(
            current_item.text() if current_item else ""
        )

    def rename_category(self):
        item = self.category_list.currentItem()

        if item is None:
            return

        old_name = item.text()

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Category",
            "Category name:",
            text=old_name
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not self.validate_category_name(
            new_name,
            original_name=old_name
        ):
            return

        if new_name == old_name:
            return

        # Replace the category name while preserving extensions and category order.
        self.rules = {
            new_name if category == old_name else category: extensions
            for category, extensions in self.rules.items()
        }

        item.setText(new_name)

        self.show_extensions(new_name)

    def rename_extension(self):
        category_item = self.category_list.currentItem()
        extension_item = self.extension_list.currentItem()

        if category_item is None or extension_item is None:
            return

        category = category_item.text()
        old_extension = extension_item.text()

        new_extension, accepted = QInputDialog.getText(
            self,
            "Rename Extension",
            "New extension:",
            text=old_extension
        )

        if not accepted:
            return

        new_extension = new_extension.strip().lower()

        if not new_extension:
            return

        if not new_extension.startswith("."):
            new_extension = "." + new_extension

        # Return without duplicate validation if the extension is unchanged.
        if new_extension == old_extension:
            return
        
        if not self.validate_extension(new_extension):
            return

        # Replace the extension in place to preserve list order.
        extensions = self.rules[category]
        index = extensions.index(old_extension)
        extensions[index] = new_extension

        self.show_extensions(category)
        self.extension_list.setCurrentRow(index)

    def add_extension(self):
        category_item = self.category_list.currentItem()

        if category_item is None:
            QMessageBox.warning(
                self,
                "No Category",
                "Select a category first."
            )
            return

        category = category_item.text()

        extension, accepted = QInputDialog.getText(
            self,
            "Add Extension",
            "Extension (for example .blend):"
        )

        if not accepted:
            return

        extension = extension.strip().lower()

        if not extension:
            return

        # Add a leading dot, converting blend to .blend.
        if not extension.startswith("."):
            extension = "." + extension

        if not self.validate_extension(extension):
            return  

        self.rules[category].append(extension)

        self.show_extensions(category)

        self.extension_list.setCurrentRow(
            self.extension_list.count() - 1
        )

    def delete_extension(self):
        category_item = self.category_list.currentItem()
        extension_item = self.extension_list.currentItem()

        if category_item is None or extension_item is None:
            return

        category = category_item.text()
        extension = extension_item.text()

        # Remove the extension from the rules copy.
        self.rules[category].remove(extension)

        # Refresh the extension list.
        self.show_extensions(category)

    def reset_rules(self):
        answer = QMessageBox.question(
            self,
            "Reset Default Rules",
            "Replace all categories and extensions with factory defaults?\n"
            "Click Save afterward to apply the changes.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        self.rules = deepcopy(DEFAULT_RULES)

        self.category_list.clear()
        self.extension_list.clear()

        self.category_list.addItems(
            list(self.rules.keys())
        )

        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)

app = QApplication(
    sys.argv
)

window = FileInsightWindow()

window.show()

sys.exit(
    app.exec()
)