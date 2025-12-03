from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

from MultiAgentGUI.components.panel_header import PanelHeader
from MultiAgentGUI.components import GenericSimulationCanvas
from MultiAgentGUI.themes import Theme


class SimulationViewPanel(QWidget):
    """
    仿真结果查看面板（只读）

    - 上方使用统一的 PanelHeader，风格与仿真区域一致
    - 下方为 GenericLayeredSceneWidget：
        - 下层：大尺寸战场 / 场景背景图
        - 上层：由上层业务（例如 mediator_service）添加的矢量 QGraphicsItem
    - 本组件本身不直接依赖后端数据结构，仅提供简单的视图接口，
      具体如何绘制矢量图由业务模块负责。
    """

    # 仿真结果查看区域的交互事件（例如点击查看、缩放等）
    # event payload 与 SimulationDesignPanel.scene_edit_requested 结构类似，
    # 仅 source 字段不同（"view" 而非 "design"）。
    scene_interaction = pyqtSignal(dict)

    def __init__(self, title: str = "仿真视图", parent=None):
        super().__init__(parent)
        self._init_ui(title)
        self._install_interaction_handlers()

    def _init_ui(self, title: str):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header：使用仿真面板专用头部配色
        header = PanelHeader(
            title,
            bg_color=Theme.PANEL_SIMULATION_HEADER_BG,
            border_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
            left_bar_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
            text_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
        )
        root_layout.addWidget(header)

        # 内容区域：使用仿真面板背景色 + 通用仿真画布
        content = QWidget()
        content.setStyleSheet(f"background-color: {Theme.PANEL_SIMULATION_BG};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
        )
        content_layout.setSpacing(Theme.SPACING_SMALL)

        self.canvas = GenericSimulationCanvas()
        content_layout.addWidget(self.canvas)

        root_layout.addWidget(content)

    def _install_interaction_handlers(self):
        """在仿真视图上安装交互回调（目前只转发鼠标点击）。"""
        # 使用 pyqtgraph 的场景点击信号获取逻辑坐标
        self.canvas.scene().sigMouseClicked.connect(self._on_mouse_clicked)

    def _on_mouse_clicked(self, ev):
        vb = self.canvas.getPlotItem().getViewBox()
        pos_in_view = vb.mapSceneToView(ev.scenePos())
        button = ev.button()
        button_name = {
            1: "left",
            2: "right",
            4: "middle",
        }.get(button, "unknown")
        payload = {
            "source": "view",
            "type": "mouse_double_click" if ev.double() else "mouse_press",
            "button": button_name,
            "scene_pos": (pos_in_view.x(), pos_in_view.y()),
            "modifiers": int(ev.modifiers()),
            "hit_count": 0,  # 如需命中测试，可在后续接入
        }
        self.scene_interaction.emit(payload)

    def get_canvas(self) -> GenericSimulationCanvas:
        """返回内部的仿真画布组件，便于上层直接调用 update_scene / set_background_image。"""
        return self.canvas



