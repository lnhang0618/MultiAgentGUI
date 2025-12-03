from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from qfluentwidgets import TableWidget
from typing import List, Any
from PyQt5.QtCore import Qt
from MultiAgentGUI.themes import Theme


class GenericTableWidget(TableWidget):
    def __init__(self, column_labels: List[str]):
        super().__init__()
        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setWordWrap(False)
        
        # 禁用交替行颜色
        self.setAlternatingRowColors(False)

        self.column_count = len(column_labels)
        self.setColumnCount(self.column_count)
        self.setHorizontalHeaderLabels(column_labels)
        self.verticalHeader().hide()

        # Header font：略大一点并加粗，但保持相对克制
        font = self.horizontalHeader().font()
        self.horizontalHeader().setFont(QFont(font.family(), font.pointSize() + 1, QFont.DemiBold))

        # Center-align headers
        for i in range(self.column_count):
            self.horizontalHeaderItem(i).setTextAlignment(Qt.AlignCenter)

        # 让所有列均匀分布宽度
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # 应用主题样式 - 背景色透明以显示panel背景
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: 1px solid {Theme.BORDER};
                border-radius: {Theme.BORDER_RADIUS}px;
                gridline-color: {Theme.BORDER_LIGHT};
                color: {Theme.TEXT_PRIMARY};
                alternate-background-color: transparent;
            }}
            QTableWidget::item {{
                border: none;
                padding: 4px;
                background-color: transparent;
            }}
            QTableWidget::item:alternate {{
                background-color: transparent;
            }}
            QTableWidget::item:selected {{
                background-color: {Theme.PRIMARY_LIGHT};
                color: {Theme.TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: {Theme.PANEL_BACKGROUND};
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-bottom: 2px solid {Theme.BORDER};
                padding: 6px;
            }}
        """)

    def set_table_data(self, data: List[List[Any]]):
        """Accepts flat 2D list. Each inner list is a row."""
        self.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table_item = QTableWidgetItem(str(item))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, table_item)

        # 数据更新后保持各列均匀宽度（Stretch 模式）