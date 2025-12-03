from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMenu
from PyQt5.QtCore import pyqtSignal

from MultiAgentGUI.components.panel_header import PanelHeader
from MultiAgentGUI.components import GenericSimulationCanvas
from MultiAgentGUI.themes import Theme


class SimulationDesignPanel(QWidget):
    """
    场景设计面板（可编辑）

    - 结构与 SimulationViewPanel 基本一致：
        - Header 使用“场景设置”风格
        - 内容为 GenericLayeredSceneWidget
    - 不直接操作业务数据结构，也不内置具体的编辑逻辑：
        - 仅负责提供一个可缩放/平移的画布
        - 具体的 item 创建 / 删除 / 修改，应由上层（例如 mediator_service）
          通过事件/回调驱动，并直接操作内部的 GenericLayeredSceneWidget
    """

    # UI → 上层（例如 mediator_service）的场景交互事件信号
    # event payload 示例（type 表示输入类型）：
    # {
    #     "source": "design",
    #     "type": "mouse_press" | "mouse_double_click" | "wheel",
    #     "button": "left" | "right" | "middle",   # 仅鼠标事件
    #     "scene_pos": (x, y),
    #     "delta": int,                            # 仅滚轮事件，angleDelta().y()
    #     "modifiers": int,                        # Qt.KeyboardModifiers 的整型值
    #     "hit_count": int,                        # 点击位置命中的 item 数量（仅鼠标）
    # }
    scene_edit_requested = pyqtSignal(dict)
    
    # 工具栏操作事件信号
    import_background_requested = pyqtSignal()  # 导入背景
    import_vector_requested = pyqtSignal()     # 导入矢量图

    def __init__(self, title: str = "场景设置", parent=None):
        super().__init__(parent)
        self._init_ui(title)
        # 安装交互事件回调，仅负责把用户意图“翻译”为事件，不做任何业务修改
        self._install_interaction_handlers()

    def _init_ui(self, title: str):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header：沿用场景设置区域的头部配色
        header = PanelHeader(
            title,
            bg_color=Theme.PANEL_SIMULATION_HEADER_BG,
            border_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
            left_bar_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
            text_color=Theme.PANEL_SIMULATION_HEADER_BORDER,
        )
        root_layout.addWidget(header)

        # 工具栏：在 header 下方添加操作栏
        toolbar = self._create_toolbar()
        root_layout.addWidget(toolbar)

        # 内容区域：使用场景设置背景色 + 通用仿真画布
        content = QWidget()
        content.setStyleSheet(f"background-color: {Theme.PANEL_SIMULATION_SCENARIO_BG};")
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
        """
        在内部 pyqtgraph 画布上安装交互回调，
        拦截鼠标点击并将其转换为通用交互事件，抛给上层。
        """
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
            "source": "design",
            "type": "mouse_double_click" if ev.double() else "mouse_press",
            "button": button_name,
            "scene_pos": (pos_in_view.x(), pos_in_view.y()),
            "modifiers": int(ev.modifiers()),
            "hit_count": 0,
        }
        self.scene_edit_requested.emit(payload)

    def _create_toolbar(self) -> QWidget:
        """创建工具栏，包含导入文件和规划器选择"""
        toolbar = QWidget()
        toolbar.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.PANEL_SIMULATION_SCENARIO_BG};
                border-bottom: 1px solid {Theme.BORDER};
            }}
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: none;
                border-radius: {Theme.BORDER_RADIUS_SMALL}px;
                padding: 6px 16px;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 9pt;
            }}
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(
            Theme.SPACING_MEDIUM,
            Theme.SPACING_SMALL,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_SMALL,
        )
        toolbar_layout.setSpacing(Theme.SPACING_MEDIUM)
        
        # 1. 导入文件按钮（带下拉菜单）
        import_button = QPushButton("导入文件")
        import_menu = QMenu(self)
        
        import_bg_action = import_menu.addAction("导入背景")
        import_bg_action.triggered.connect(self.import_background_requested.emit)
        
        import_vector_action = import_menu.addAction("导入矢量图")
        import_vector_action.triggered.connect(self.import_vector_requested.emit)
        
        import_button.setMenu(import_menu)
        toolbar_layout.addWidget(import_button)
        
        # 添加弹性空间，让右侧保持空白（规划器选择已移到浮窗）
        toolbar_layout.addStretch(1)
        
        return toolbar
    
    def get_canvas(self) -> GenericSimulationCanvas:
        """返回内部的仿真画布组件，便于上层直接调用 update_scene / set_background_image。"""
        return self.canvas



