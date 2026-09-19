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

from organizer import analyze_folder, organize_files
from file_stats import format_size


class FileInsightWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_folder = None

        self.setWindowTitle("FileInsight")
        self.resize(1100, 750)

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

        self.path_label = QLabel(
            "No folder selected"
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

        self.analyze_button.setEnabled(
            False
        )

        self.organize_button.setEnabled(
            False
        )

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

        self.browse_button.clicked.connect(
            self.select_folder
        )

        self.analyze_button.clicked.connect(
            self.analyze_selected_folder
        )

        self.organize_button.clicked.connect(
            self.organize_selected_folder
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
            self.empty_label
        )

        self.m_layout.addWidget(
            self.stats_table
        )

        self.m_layout.addLayout(
            self.chart_layout
        )

        self.m_layout.addWidget(
            self.status_label
        )

        self.setLayout(
            self.m_layout
        )

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

    def analyze_selected_folder(self):
        if self.selected_folder is None:
            return

        self.status_label.setText(
            "Status: Analyzing..."
        )

        stats = analyze_folder(
            self.selected_folder
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

        self.status_label.setText(
            "Status: Organizing..."
        )

        stats, output_root = organize_files(
            self.selected_folder
        )

        self.update_stats_table(
            stats
        )

        self.update_charts(
            stats
        )

        self.show_statistics()

        self.status_label.setText(
            f"Status: Done - {output_root}"
        )

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


app = QApplication(
    sys.argv
)

window = FileInsightWindow()

window.show()

sys.exit(
    app.exec()
)