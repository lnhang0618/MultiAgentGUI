# components/panel_header.py
"""
面板标题栏组件
为每个面板提供统一的标题栏显示
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import BodyLabel
from MultiAgentGUI.themes import Theme


class PanelHeader(QWidget):
    """
    面板标题栏组件
    显示面板的中文名称，提供统一的视觉风格
    """
    
    def __init__(
        self,
        title: str,
        parent=None,
        *,
        bg_color: str = None,
        border_color: str = None,
        left_bar_color: str = None,
        text_color: str = None,
    ):
        """
        初始化面板标题栏
        
        参数：
            title: 面板的中文名称
            parent: 父组件
            bg_color: 标题栏背景色（不传则使用默认主色方案）
            border_color: 下边框颜色
            left_bar_color: 左侧竖条颜色
            text_color: 标题文字颜色
        """
        super().__init__(parent)
        self._title = title
        self._bg_color = bg_color
        self._border_color = border_color
        self._left_bar_color = left_bar_color
        self._text_color = text_color
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        # 增大上下边距，让标题栏在视觉上更“厚重”一点
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(0)
        
        # 创建标题标签
        self.title_label = QLabel(self._title)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        # 放大字号 + 加粗，让标题更醒目
        font.setPointSize(15)          # 比普通内容明显更大
        font.setWeight(QFont.Bold)     # 使用更粗的字重
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # 居中显示
        
        layout.addStretch()  # 左侧弹性空间
        layout.addWidget(self.title_label)
        layout.addStretch()  # 右侧弹性空间，使标题居中
        
        # 优先使用显式传入的颜色，否则退回到默认的主色风格
        header_bg = self._bg_color or Theme.PRIMARY_LIGHT
        border_color = self._border_color or Theme.PRIMARY
        left_bar_color = self._left_bar_color or border_color
        text_color = self._text_color or Theme.PRIMARY

        self.setStyleSheet(f"""
            PanelHeader {{
                background-color: {header_bg};
                border-bottom: 2px solid {border_color};
                border-left: 4px solid {left_bar_color};
                border-top-left-radius: {Theme.BORDER_RADIUS}px;
                border-top-right-radius: {Theme.BORDER_RADIUS}px;
            }}
            QLabel {{
                color: {text_color};
                background-color: transparent;
            }}
        """)
    
    def set_title(self, title: str):
        """设置标题文本"""
        self._title = title
        self.title_label.setText(title)

