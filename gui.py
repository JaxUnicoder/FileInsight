import sys
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtCore import Qt
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
    QAbstractItemView
)

from organizer import organize_files
from file_stats import format_size


class FileInsightWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_folder = None

        self.setWindowTitle("FileInsight")
        self.resize(1100, 750)

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

        self.bar_figure = Figure()
        self.bar_canvas = FigureCanvas(self.bar_figure)

        self.pie_figure = Figure()
        self.pie_canvas = FigureCanvas(self.pie_figure)

        self.chart_layout = QHBoxLayout()
        self.chart_layout.addWidget(self.bar_canvas)
        self.chart_layout.addWidget(self.pie_canvas)

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

        self.layout.addLayout(self.chart_layout)

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
        self.update_charts(stats)

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

    def update_charts(self, stats):
        categories = []
        sizes_mb = []

        for category, data in stats.items():
            categories.append(category)
            sizes_mb.append(
                data["size"] / (1024 ** 2)
            )

        self.bar_figure.clear()

        bar_axes = self.bar_figure.add_subplot(111)

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
                pie_labels.append(category)
                pie_sizes.append(data["size"])

        self.pie_figure.clear()

        pie_axes = self.pie_figure.add_subplot(111)

        if pie_sizes:
            pie_axes.pie(
                pie_sizes,
                labels=pie_labels,
                autopct="%1.1f%%"
            )

        pie_axes.set_title(
            "Storage Distribution"
        )

        self.pie_figure.tight_layout()

        self.pie_canvas.draw()


app = QApplication(sys.argv)

window = FileInsightWindow()
window.show()

sys.exit(app.exec())