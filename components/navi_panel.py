# ui/widgets/navigation_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import SegmentedWidget


class NavigationPanel(QWidget):
    """通用分段导航面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 5, 0, 0)

        self.pivot = SegmentedWidget(self)
        self.stacked_widget = QStackedWidget(self)

        self.layout().addWidget(self.pivot)
        self.layout().addWidget(self.stacked_widget)

    def add_page(self, widget: QWidget, route_key: str, title: str):
        """添加一个页面"""
        widget.setObjectName(route_key)
        self.stacked_widget.addWidget(widget)
        self.pivot.addItem(
            routeKey=route_key,
            text=title,
            onClick=lambda: self.stacked_widget.setCurrentWidget(widget)
        )

    def set_current_page(self, route_key: str):
        """设置当前页面"""
        self.pivot.setCurrentItem(route_key)