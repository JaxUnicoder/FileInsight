import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)

from organizer import organize_files
from file_stats import format_size


class FileInsightWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_folder = None

        self.setWindowTitle("FileInsight")
        self.resize(700, 450)

        self.layout = QVBoxLayout()

        self.title_label = QLabel("FileInsight")
        self.path_label = QLabel("No folder selected")
        self.status_label = QLabel("Status: Ready")

        self.title_label.setAlignment(Qt.AlignCenter)

        self.browse_button = QPushButton("Browse")
        self.organize_button = QPushButton("Organize Files")

        self.organize_button.setEnabled(False)

        self.stats_table = QTableWidget()

        self.setup_table()

        self.browse_button.clicked.connect(
            self.select_folder
        )

        self.organize_button.clicked.connect(
            self.organize_selected_folder
        )

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.path_label)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.organize_button)
        self.layout.addWidget(self.stats_table)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

    def setup_table(self):
        self.stats_table.setColumnCount(3)

        self.stats_table.setHorizontalHeaderLabels(
            ["Category", "Files", "Size"]
        )

        self.stats_table.verticalHeader().setVisible(False)

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
            self.selected_folder = Path(folder_path)

            self.path_label.setText(
                f"Folder: {self.selected_folder}"
            )

            self.organize_button.setEnabled(True)

            self.status_label.setText(
                "Status: Folder selected"
            )

    def organize_selected_folder(self):
        if self.selected_folder is None:
            return

        self.status_label.setText(
            "Status: Organizing..."
        )

        stats, output_root = organize_files(
            self.selected_folder
        )

        self.update_stats_table(stats)

        self.status_label.setText(
            f"Status: Done - {output_root}"
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
                format_size(data["size"])
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


app = QApplication(sys.argv)

window = FileInsightWindow()
window.show()

sys.exit(app.exec())