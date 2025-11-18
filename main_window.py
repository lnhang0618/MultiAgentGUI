from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from ui.UI_HomeInterface import Ui_HomeInterface
from panels import TaskInfoPanel, AgentInfoPanel, CommandPanel
from components.generic_simul_canvas import GenericSimulationCanvas
from typing import Optional
from services import MediatorService
from example_mediator_service import ExampleMediatorService

class MainWindow(Ui_HomeInterface, QWidget):
    def __init__(self, mediator: Optional[MediatorService] = None, parent=None):
        """
        初始化主窗口
        
        参数：
            mediator: 中介服务实例（MediatorService）。如果为None，则使用ExampleMediatorService作为默认值（仅用于向后兼容）
            parent: 父组件
        """
        super().__init__(parent=parent)
        self.setupUi(self)
        # 依赖注入：如果没有提供mediator，使用ExampleMediatorService（向后兼容）
        if mediator is None:
            mediator = ExampleMediatorService()
        self._mediator = mediator
        self.init_sub_widgets()
        self.init_data_refresh()
        # 初始数据加载
        self.refresh_all_panels()

    def init_sub_widgets(self):
        """初始化子面板"""
        # 创建子面板
        self.task_panel = TaskInfoPanel()
        self.agent_panel = AgentInfoPanel()
        self.simulation_canvas = GenericSimulationCanvas()
        # CommandPanel直接使用MediatorService（实现CommandHandler接口）
        self.command_panel = CommandPanel(self._mediator)

        # 为每个容器设置布局并添加子部件
        self._setup_widget_container(self.TaskInfoWidget, self.task_panel)
        self._setup_widget_container(self.AgentInfoWidget, self.agent_panel)
        self._setup_widget_container(self.SimulationWidget, self.simulation_canvas)
        self._setup_widget_container(self.CommandWidget, self.command_panel)

        # 设置阴影（注意：阴影应作用于容器，不是子面板）
        for widget in [self.SimulationWidget, self.CommandWidget]:
            self._setShadowEffect(widget)
        
        # 连接CommandPanel的信号：当命令执行成功时刷新数据
        self.command_panel.command_executed.connect(self.refresh_all_panels)
        
        # 初始化命令面板的选项数据
        self._refresh_command_panel_options()
    
    def init_data_refresh(self):
        """初始化数据刷新定时器"""
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_all_panels)
        self._refresh_timer.start(1000)  # 每1秒刷新一次
        
        # 仿真时间更新定时器
        self._simulation_timer = QTimer(self)
        self._simulation_timer.timeout.connect(self._update_simulation_time)
        self._simulation_timer.start(100)  # 每100ms更新一次仿真时间
    
    def refresh_all_panels(self):
        """刷新所有面板的数据"""
        # 刷新Agent数据
        agent_data = self._mediator.fetch_agent_data()
        self.agent_panel.load_data(agent_data)
        
        # 刷新Task数据
        task_data = self._mediator.fetch_task_data()
        self.task_panel.load_data(task_data)
        
        # 刷新仿真场景数据
        scene_data = self._mediator.fetch_simulation_scene()
        self.simulation_canvas.update_scene(scene_data)
        
        # 刷新命令面板选项（任务ID和命令选项可能会变化）
        self._refresh_command_panel_options()
    
    def _update_simulation_time(self):
        """
        更新仿真时间（仅当仿真运行时）
        
        注意：时间步管理完全由中介服务负责，前端只负责触发。
        这样可以确保：
        1. 时间步长由中介服务决定（固定步长、自适应步长等）
        2. 数据更新与时间步同步
        3. 不同中介服务可以有不同的时间步策略
        """
        # 检查仿真是否运行（通过中介服务接口，不访问私有属性）
        if self._mediator.is_simulation_running():
            # 让中介服务推进一个时间步（时间步长由中介服务决定）
            self._mediator.step_simulation()
            # 更新场景（因为位置可能改变）
            scene_data = self._mediator.fetch_simulation_scene()
            self.simulation_canvas.update_scene(scene_data)
    
    def _refresh_command_panel_options(self):
        """刷新命令面板的选项数据"""
        # 更新任务模板
        templates = self._mediator.get_task_templates()
        self.command_panel.set_task_template_options(templates)
        
        # 更新任务ID列表
        task_ids = self._mediator.get_task_ids()
        self.command_panel.set_task_id_selection_options(task_ids)
        
        # 更新命令选项
        commands = self._mediator.get_command_options()
        self.command_panel.set_command_selection_options(commands)

    def _setup_widget_container(self, container: QWidget, child: QWidget):
        """将 child 添加到 container 中，并设置布局"""
        layout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)  # 去掉边距，避免空白
            layout.setSpacing(0)
        # 清空原有内容（可选）
        while layout.count():
            layout.takeAt(0).widget().deleteLater()
        layout.addWidget(child)
        container.setLayout(layout)

    def _setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 0))
        shadowEffect.setBlurRadius(8)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)
    
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 依赖注入：在__main__中创建mediator并注入到MainWindow
    # 这样可以灵活切换不同的中介服务实现（ExampleMediatorService, RestApiMediatorService, DatabaseMediatorService等）
    mediator = ExampleMediatorService()
    main_window = MainWindow(mediator=mediator)
    main_window.show()
    
    sys.exit(app.exec_())
