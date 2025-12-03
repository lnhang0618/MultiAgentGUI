import sys
from pathlib import Path

# Add parent directory to path when running as script
# This allows the script to find MultiAgentGUI module when run directly
_script_file = Path(__file__).resolve()
try:
    _main_file = Path(sys.argv[0]).resolve()
    # If this file is being run directly, add parent to path
    if _script_file == _main_file:
        parent_dir = _script_file.parent.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
except (IndexError, OSError):
    # If sys.argv[0] is not available or path doesn't exist, skip
    pass

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QSizePolicy
from qfluentwidgets import CardWidget

from MultiAgentGUI.panels import (
    PlaceholderPanel,
    TaskInfoPanel,
    AgentInfoPanel,
    CommandPanel,
    SimulationViewPanel,
    SimulationDesignPanel,
    PlannerFloatingPanel,
)
from MultiAgentGUI.animations.transition import FadeTransitionManager
from MultiAgentGUI.themes import Theme


class ViewMode:
    LAYOUT = "layout"
    VIEW = "view"


class MainWindow(QWidget):
    """
    使用 PlaceholderPanel 的新主窗口。
    - 支持"布局模式"和"查看模式"两种视图
    - 右下角有一个按钮：开始仿真 / 暂停仿真，用于在两种模式间切换
    - 只负责 UI 组装，不包含业务逻辑
    - 业务逻辑和 Mediator 交互由 MainWindowController 负责
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 基础属性，与原 UI_HomeInterface 中保持一致，方便复用样式表
        self.setObjectName("HomeInterface")
        # 调整默认窗口尺寸，让初始布局更舒展
        self.resize(1500, 900)

        # 直接在代码中构建基础布局，不再依赖 UI_HomeInterface
        self._build_base_layout()

        self._mode = ViewMode.LAYOUT
        self._transition = FadeTransitionManager(self)

        self._init_panels()
        self._init_mode_button()
        self._init_planner_floating_panel()
        
        self._apply_theme()
        self._apply_mode_layout()

    # --- 初始化子面板 ---
    def _build_base_layout(self):
        """
        创建主窗口的基础网格布局和几个 CardWidget 容器。

        这里基本等价于之前 UI_HomeInterface.setupUi 里做的事情，
        只是更简化、且完全在代码中可控。
        """
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(12)
        self.gridLayout.setContentsMargins(12, 12, 12, 12)

        # 仿真区域容器
        self.SimulationWidget = CardWidget(self)
        self.SimulationWidget.setEnabled(True)
        sp = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.SimulationWidget.setSizePolicy(sp)
        self.SimulationWidget.setMinimumSize(500, 0)
        self.SimulationWidget.setObjectName("SimulationWidget")

        # 场景设计容器
        self.SimulationScenarioWidget = CardWidget(self)
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.SimulationScenarioWidget.setSizePolicy(sp)
        self.SimulationScenarioWidget.setMinimumSize(500, 0)
        self.SimulationScenarioWidget.setObjectName("SimulationScenarioWidget")

        # 命令输入容器
        self.CommandWidget = CardWidget(self)
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.CommandWidget.setSizePolicy(sp)
        # 与场景设计区域保持一致的最小宽度，避免看起来更窄
        self.CommandWidget.setMinimumSize(500, 0)
        self.CommandWidget.setObjectName("CommandWidget")

        # 任务信息容器
        self.TaskInfoWidget = CardWidget(self)
        sp = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.TaskInfoWidget.setSizePolicy(sp)
        # 与其它区域保持一致的最小宽度，避免右侧看起来更宽
        self.TaskInfoWidget.setMinimumSize(500, 0)
        self.TaskInfoWidget.setObjectName("TaskInfoWidget")

        # 智能体信息容器
        self.AgentInfoWidget = CardWidget(self)
        sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.AgentInfoWidget.setSizePolicy(sp)
        self.AgentInfoWidget.setMinimumSize(500, 0)
        self.AgentInfoWidget.setObjectName("AgentInfoWidget")

        # 具体的行列布局在 _apply_mode_layout 中统一设置，这里只负责创建容器本身

    def _init_panels(self):
        """初始化各个功能面板"""
        # 仿真结果查看：只读场景视图
        self.sim_panel = SimulationViewPanel(title="仿真视图")
            # 场景设计：可编辑场景视图（编辑逻辑由 MainWindowController 协调，Mediator 处理）
        self.sim_scenario_panel = SimulationDesignPanel(title="场景设置")
        # 使用真实的任务 / 智能体信息面板，替换占位面板
        self.task_panel = TaskInfoPanel()
        self.agent_panel = AgentInfoPanel()
        # 命令输入区域：使用新的精简版命令面板（文本输入 + 按钮 + 两个模板下拉框）
        self.command_panel = CommandPanel()

        # 将占位面板嵌入到 UI 容器中
        self._setup_widget_container(self.SimulationWidget, self.sim_panel)
        self._setup_widget_container(self.SimulationScenarioWidget, self.sim_scenario_panel)
        self._setup_widget_container(self.TaskInfoWidget, self.task_panel)
        self._setup_widget_container(self.AgentInfoWidget, self.agent_panel)
        self._setup_widget_container(self.CommandWidget, self.command_panel)

    def _setup_widget_container(self, container: QWidget, child: QWidget):
        """为容器设置统一的内边距和布局，并添加子部件"""
        layout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
        layout.setContentsMargins(
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
        )
        layout.setSpacing(Theme.SPACING_SMALL)
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        layout.addWidget(child)
        container.setLayout(layout)

    # 注意：Mediator 绑定与数据刷新已移至 MainWindowController
    # MainWindow 只负责 UI 组装，不直接与 Mediator 交互

    # --- 右下角模式切换按钮 ---
    def _init_mode_button(self):
        self._mode_button = QPushButton(self)
        # 与命令面板的“确认发送”按钮使用同一视觉风格
        self._mode_button.setObjectName("PrimaryActionButton")
        self._mode_button.setCursor(Qt.PointingHandCursor)
        self._mode_button.clicked.connect(self._toggle_mode)
        self._update_mode_button_text()
        self._position_mode_button()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_mode_button()
        if hasattr(self, '_planner_panel') and self._planner_panel.isVisible():
            self._position_planner_panel()

    def _position_mode_button(self):
        """将按钮放在窗口右下角，保留一定边距"""
        margin = 24
        # 放大按钮尺寸，便于点击
        btn_w = 220
        btn_h = 44
        x = self.width() - btn_w - margin
        y = self.height() - btn_h - margin
        self._mode_button.setGeometry(x, y, btn_w, btn_h)
    
    def _init_planner_floating_panel(self):
        """初始化规划器选择浮窗"""
        # 使用独立的 panel 类
        self._planner_panel = PlannerFloatingPanel(self)
        
        # 注意：planner_selected 信号由 Controller 连接，MainWindow 不处理业务逻辑
        
        # 初始位置
        self._position_planner_panel()
    
    def _position_planner_panel(self):
        """定位规划器浮窗，放在开始仿真按钮的左边"""
        if not hasattr(self, '_mode_button') or not hasattr(self, '_planner_panel'):
            return
        
        margin = 24
        btn_w = 220
        btn_x = self.width() - btn_w - margin
        btn_y = self.height() - 44 - margin  # 按钮高度是 44
        
        # 使用 panel 的 update_position 方法
        self._planner_panel.update_position(self.width(), self.height(), btn_x, btn_y)
    

    def _update_mode_button_text(self):
        if self._mode == ViewMode.LAYOUT:
            self._mode_button.setText("开始仿真（切换到查看模式）")
        else:
            self._mode_button.setText("暂停仿真（切换到布局模式）")
        # 稍微放大字体，由字体控制而不是覆盖样式表
        font = self._mode_button.font()
        font.setPointSize(11)
        font.setBold(True)
        self._mode_button.setFont(font)

    # --- 模式切换 ---
    def _toggle_mode(self):
        """点击按钮在布局模式 / 查看模式之间切换"""
        self._mode = ViewMode.VIEW if self._mode == ViewMode.LAYOUT else ViewMode.LAYOUT

        # 参与动画的所有面板
        all_panels = [
            self.SimulationWidget,
            self.SimulationScenarioWidget,
            self.CommandWidget,
            self.TaskInfoWidget,
            self.AgentInfoWidget,
        ]

        # 第 0 阶段：先隐藏/显示规划器浮窗（立即执行，不参与动画）
        if hasattr(self, '_planner_panel'):
            if self._mode == ViewMode.VIEW:
                # 切换到查看模式：先隐藏浮窗
                self._planner_panel.hide()
            # 注意：浮窗的显示会在 _after_fade_out 中延迟执行

        # 第 1 阶段：让当前可见的面板统一慢慢淡出
        currently_visible = [w for w in all_panels if w.isVisible()]

        def _after_fade_out():
            # 中间阶段：切换到目标模式的布局
            self._apply_mode_layout()
            self._update_mode_button_text()

            # 根据新模式下的可见性，决定要淡入哪些面板
            target_visible = [w for w in all_panels if w.isVisible()]

            # 第 2 阶段：让新布局中的面板淡入出现
            self._transition.fade_widgets(to_show=target_visible, to_hide=[])

            # 第 3 阶段：如果是布局模式，延迟显示浮窗（在其他面板淡入之后）
            if self._mode == ViewMode.LAYOUT and hasattr(self, '_planner_panel'):
                QTimer.singleShot(300, lambda: self._planner_panel.show())  # 延迟300ms显示

        self._transition.fade_widgets(
            to_show=[],
            to_hide=currently_visible,
            finished_callback=_after_fade_out,
        )

    def _apply_mode_layout(self):
        """
        根据当前模式调整各面板的可见性与布局权重。
        先实现基础的"显隐 + 拉伸因子"切换，后续再加动画。
        """
        if not hasattr(self, "gridLayout"):
            return
        
        # 注意：规划器浮窗的显示/隐藏已在 _toggle_mode 中处理
        # 这里只负责定位（如果浮窗可见的话）
        if hasattr(self, '_planner_panel') and self._planner_panel.isVisible():
            self._position_planner_panel()

        if self._mode == ViewMode.LAYOUT:
            # 布局模式：不显示仿真主界面，仅用于配置场景与任务
            self.SimulationWidget.setVisible(False)
            self.SimulationScenarioWidget.setVisible(True)
            self.CommandWidget.setVisible(True)
            self.TaskInfoWidget.setVisible(True)
            self.AgentInfoWidget.setVisible(True)

            # 逻辑网格：4 行 × 6 列
            # 左侧（0-3 列）：配置相关
            #   - 场景调整：左侧上 3 行 × 4 列（第 0-2 行, 第 0-3 列）
            #   - 命令输入：左侧第 4 行 × 4 列（第 3 行, 第 0-3 列）
            # 右侧（4-5 列）：信息展示
            #   - 任务信息：右侧上 2 行 × 2 列（第 0-1 行, 第 4-5 列）
            #   - 智能体信息：右侧下 2 行 × 2 列（第 2-3 行, 第 4-5 列）
            self.gridLayout.addWidget(self.SimulationScenarioWidget, 0, 0, 3, 4)
            self.gridLayout.addWidget(self.CommandWidget, 3, 0, 1, 4)
            self.gridLayout.addWidget(self.TaskInfoWidget, 0, 4, 2, 2)
            self.gridLayout.addWidget(self.AgentInfoWidget, 2, 4, 2, 2)

            # 列、行拉伸均匀，左侧 4 列 / 右侧 2 列 ≈ 2:1，高度 4 行平均分配
            for col in range(6):
                self.gridLayout.setColumnStretch(col, 1)
            for row in range(4):
                self.gridLayout.setRowStretch(row, 1)
        else:
            # 查看模式：
            # 逻辑上将网格视为 2 行 x 6 列：
            # - 仿真主视图占据左侧 2 行 x 4 列（第0-1行, 第0-3列）
            # - 任务信息占据右上 1 行 x 2 列（第0行, 第4-5列）
            # - 智能体信息占据右下 1 行 x 2 列（第1行, 第4-5列）
            self.SimulationWidget.setVisible(True)
            self.SimulationScenarioWidget.setVisible(False)
            self.CommandWidget.setVisible(False)
            self.TaskInfoWidget.setVisible(True)
            self.AgentInfoWidget.setVisible(True)

            # 仿真视图：4 行 × 4 列
            self.gridLayout.addWidget(self.SimulationWidget, 0, 0, 4, 4)
            # 任务信息：上方 2 行 × 2 列
            self.gridLayout.addWidget(self.TaskInfoWidget, 0, 4, 2, 2)
            # 智能体信息：下方 2 行 × 2 列
            self.gridLayout.addWidget(self.AgentInfoWidget, 2, 4, 2, 2)

            # 设置 6 列的拉伸比例全部相同：
            # 列宽相等时，仿真视图占 4 列、信息栏占 2 列 → 宽度约为 2:1
            for col in range(6):
                self.gridLayout.setColumnStretch(col, 1)

            # 行拉伸使用 Qt 默认行为，让两行自动按内容和跨行情况分配高度

    # --- 主题 ---
    def _apply_theme(self):
        """应用与旧主窗口一致的主题设置"""
        base_styles = Theme.get_global_stylesheet()
        # 在全局样式基础上，仅追加对 HomeInterface 根窗口背景色的补充，
        # 避免对按钮等子控件做任何额外覆盖。
        self.setStyleSheet(
            base_styles
            + f"""
            QWidget#HomeInterface {{
                background-color: {Theme.BACKGROUND};
            }}
            """
        )


