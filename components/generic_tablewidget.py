from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidgetItem
from qfluentwidgets import TableWidget
from typing import List, Any
from PyQt5.QtCore import Qt


class GenericTableWidget(TableWidget):
    def __init__(self, column_labels: List[str]):
        super().__init__()
        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setWordWrap(False)

        self.column_count = len(column_labels)
        self.setColumnCount(self.column_count)
        self.setHorizontalHeaderLabels(column_labels)
        self.verticalHeader().hide()

        # Bold header font
        font = self.horizontalHeader().font()
        self.horizontalHeader().setFont(QFont(font.family(), font.pointSize() + 1, QFont.DemiBold))

        # Center-align headers
        for i in range(self.column_count):
            self.horizontalHeaderItem(i).setTextAlignment(Qt.AlignCenter)

        self.horizontalHeader().setStretchLastSection(True)
        self.resizeColumnsToContents()
        self.setStyleSheet("background-color: white;")

    def set_table_data(self, data: List[List[Any]]):
        """Accepts flat 2D list. Each inner list is a row."""
        self.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, table_item)

        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(0)
        self.horizontalHeader().setStretchLastSection(True)