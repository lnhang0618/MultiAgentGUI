# panels/placeholder_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from MultiAgentGUI.components.panel_header import PanelHeader
from MultiAgentGUI.themes import Theme


class PlaceholderPanel(QWidget):
    """
    统一的占位面板，确保布局稳定且主题一致。
    当 supports_simulation=True 时，会实现 show_vector_scene/show_image 接口，
    以兼容 main_window 中的仿真刷新逻辑。
    """

    def __init__(
        self,
        title: str = "占位面板",
        message: str = "该区域暂未实现",
        *,
        supports_simulation: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._supports_simulation = supports_simulation
        self._init_ui(title, message)

    def _init_ui(self, title: str, message: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 占位面板主体使用仿真面板背景色，header 使用 Theme 中专门配置的 header 颜色
        self.header = PanelHeader(
            title,
            bg_color=Theme.PANEL_SIMULATION_HEADER_BG,
            border_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
            left_bar_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
            # 标题文字使用该面板的主题深色，而不是全局主文字色
            text_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
        )
        layout.addWidget(self.header)

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {Theme.PANEL_SIMULATION_BG};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(Theme.SPACING_MEDIUM, Theme.SPACING_MEDIUM,
                                          Theme.SPACING_MEDIUM, Theme.SPACING_MEDIUM)

        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: rgba(255, 255, 255, 0.65); font-size: 16px;")
        label.setWordWrap(True)
        content_layout.addWidget(label)

        layout.addWidget(content_widget)

    # --- 仿真接口的空实现，保障 main_window 兼容 ---
    def show_vector_scene(self, scene_data) -> bool:
        """
        保持与旧 SimulationPanel 相同的接口，方便主窗口复用刷新逻辑。
        """
        if not self._supports_simulation:
            return False
        return False

    def show_image(self, image_path):
        if not self._supports_simulation:
            return
        # 无内容显示，占位即可
        return


