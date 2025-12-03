from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt5.QtCore import pyqtSignal, Qt

from qfluentwidgets import ComboBox
from MultiAgentGUI.themes import Theme


class PlannerFloatingPanel(QFrame):
    """
    规划器选择浮窗面板
    
    显示在窗口右下角，包含红方和蓝方规划器的选择下拉框。
    在布局模式下显示，在查看模式下隐藏。
    """
    
    # 规划器选择变化信号
    planner_selected = pyqtSignal(str, str)  # (faction, planner_name)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.CARD_BACKGROUND};
                border: 2px solid {Theme.PRIMARY};
                border-radius: {Theme.BORDER_RADIUS}px;
                padding: 12px;
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 9pt;
            }}
        """)
        
        # 创建布局
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(10)
        
        # 标题（无边框，纯文本）
        title_label = QLabel("选择规划器")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                border: none;
                color: {Theme.TEXT_PRIMARY};
                padding: 0px;
            }}
        """)
        panel_layout.addWidget(title_label)
        
        # 红方规划器
        red_layout = QHBoxLayout()
        red_layout.setSpacing(8)
        red_layout.setContentsMargins(0, 0, 0, 0)
        red_label = QLabel("红方规划器：")
        red_label.setFixedWidth(80)  # 固定宽度，确保对齐
        red_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                border: none;
                color: {Theme.TEXT_PRIMARY};
                font-size: 9pt;
                padding: 0px;
            }}
        """)
        red_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)  # 右对齐，让冒号对齐
        self._red_planner_combo = ComboBox()
        self._red_planner_combo.setMinimumWidth(120)
        self._red_planner_combo.setMinimumHeight(32)  # 设置最小高度，让下拉框更高
        self._red_planner_combo.currentTextChanged.connect(
            lambda text: self.planner_selected.emit("red", text)
        )
        red_layout.addWidget(red_label)
        red_layout.addWidget(self._red_planner_combo)
        red_layout.addStretch()  # 右侧弹性空间
        panel_layout.addLayout(red_layout)
        
        # 蓝方规划器
        blue_layout = QHBoxLayout()
        blue_layout.setSpacing(8)
        blue_layout.setContentsMargins(0, 0, 0, 0)
        blue_label = QLabel("蓝方规划器：")
        blue_label.setFixedWidth(80)  # 固定宽度，确保对齐
        blue_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                border: none;
                color: {Theme.TEXT_PRIMARY};
                font-size: 9pt;
                padding: 0px;
            }}
        """)
        blue_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)  # 右对齐，让冒号对齐
        self._blue_planner_combo = ComboBox()
        self._blue_planner_combo.setMinimumWidth(120)
        self._blue_planner_combo.setMinimumHeight(32)  # 设置最小高度，让下拉框更高
        self._blue_planner_combo.currentTextChanged.connect(
            lambda text: self.planner_selected.emit("blue", text)
        )
        blue_layout.addWidget(blue_label)
        blue_layout.addWidget(self._blue_planner_combo)
        blue_layout.addStretch()  # 右侧弹性空间
        panel_layout.addLayout(blue_layout)
    
    def set_planner_options(self, red_planners: list, blue_planners: list):
        """设置规划器选项"""
        self._red_planner_combo.clear()
        if red_planners:
            self._red_planner_combo.addItems(red_planners)
        
        self._blue_planner_combo.clear()
        if blue_planners:
            self._blue_planner_combo.addItems(blue_planners)
    
    def update_position(self, parent_width: int, parent_height: int, button_x: int, button_y: int):
        """更新浮窗位置，放在按钮的左边"""
        margin = 24
        panel_width = 240
        panel_height = 120
        spacing = 12  # 浮窗和按钮之间的间距
        vertical_offset = -40  # 上移40像素
        
        # 浮窗位置：在按钮左边，并上移
        panel_x = button_x - panel_width - spacing
        panel_y = button_y - (panel_height - 44) // 2 + vertical_offset  # 按钮高度是 44
        
        self.setGeometry(panel_x, panel_y, panel_width, panel_height)

