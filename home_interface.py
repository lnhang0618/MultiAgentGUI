from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QVBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from ui.UI_HomeInterface import Ui_HomeInterface
from task_panel import TaskInfoPanel
from agent_panel import AgentInfoPanel
from components.generic_simul_canvas import GenericSimulationCanvas
from command_interface import CommandInterface
from typing import Optional
from services import (
    BackendAdapter,
    AgentService,
    TaskService,
    CommandService,
    SimulationService
)
from example_backend_adapter import ExampleBackendAdapter

class HomeInterface(Ui_HomeInterface, QWidget):
    def __init__(self, backend: Optional[BackendAdapter] = None, parent=None):
        """
        初始化主界面
        
        参数：
            backend: 后端适配器实例。如果为None，则使用ExampleBackendAdapter作为默认值（仅用于向后兼容）
            parent: 父组件
        """
        super().__init__(parent=parent)
        self.setupUi(self)
        # 依赖注入：如果没有提供backend，使用ExampleBackendAdapter（向后兼容）
        if backend is None:
            backend = ExampleBackendAdapter()
        self.init_services(backend)
        self.init_sub_widgets()
        self.init_data_refresh()
        # 初始数据加载
        self.refresh_all_data()

    def init_services(self, backend: BackendAdapter):
        """
        初始化Service层
        
        参数：
            backend: 后端适配器实例（通过依赖注入传入）
        """
        self._backend = backend
        
        # 创建各个Service
        self._agent_service = AgentService(self._backend)
        self._task_service = TaskService(self._backend)
        self._command_service = CommandService(self._backend)
        self._simulation_service = SimulationService(self._backend)
    
    def init_sub_widgets(self):
        """初始化子面板"""
        # 创建子面板
        self.task_panel = TaskInfoPanel()
        self.agent_panel = AgentInfoPanel()
        self.simulation_canvas = GenericSimulationCanvas()
        self.command_panel = CommandInterface()

        # 为每个容器设置布局并添加子部件
        self._setup_widget_container(self.TaskInfoWidget, self.task_panel)
        self._setup_widget_container(self.AgentInfoWidget, self.agent_panel)
        self._setup_widget_container(self.SimulationWidget, self.simulation_canvas)
        self._setup_widget_container(self.CommandWidget, self.command_panel)

        # 设置阴影（注意：阴影应作用于容器，不是子面板）
        for widget in [self.SimulationWidget, self.CommandWidget]:
            self._setShadowEffect(widget)
        
        # 初始化命令面板的选项数据
        self._update_command_panel_options()
    
    def init_data_refresh(self):
        """初始化数据刷新定时器"""
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_all_data)
        self._refresh_timer.start(1000)  # 每1秒刷新一次
        
        # 仿真时间更新定时器
        self._simulation_timer = QTimer(self)
        self._simulation_timer.timeout.connect(self._update_simulation_time)
        self._simulation_timer.start(100)  # 每100ms更新一次仿真时间
    
    def refresh_all_data(self):
        """刷新所有面板的数据"""
        # 刷新Agent数据
        coalition_data = self._agent_service.get_coalition_data_for_gui()
        friendly_agent_data = self._agent_service.get_friendly_agent_data_for_gui()
        enemy_agent_data = self._agent_service.get_enemy_agent_data_for_gui()
        unit_gantt_data = self._agent_service.get_unit_gantt_data_for_gui()
        replan_options = self._agent_service.get_replan_gantt_options()
        replan_data_map = self._agent_service.get_replan_gantt_data_for_gui()
        
        self.agent_panel.set_coalition_data(coalition_data)
        self.agent_panel.set_friendly_agent_data(friendly_agent_data)
        self.agent_panel.set_enemy_agent_data(enemy_agent_data)
        self.agent_panel.set_unit_gantt_data(unit_gantt_data)
        self.agent_panel.set_replan_gantt_options(replan_options)
        for option_key, data in replan_data_map.items():
            self.agent_panel.set_replan_gantt_data(option_key, data)
        
        # 刷新Task数据
        table_data, gantt_data, ltl_text = self._task_service.get_task_data_for_gui()
        self.task_panel.set_task_data(table_data, gantt_data, ltl_text)
        
        # 刷新仿真场景数据
        scene_data = self._simulation_service.get_scene_data_for_gui()
        self.simulation_canvas.update_scene(scene_data)
    
    def _update_simulation_time(self):
        """更新仿真时间（仅当仿真运行时）"""
        if self._backend._simulation_running:
            self._backend.update_time(0.1)  # 每次增加0.1秒
            # 更新场景（因为位置可能改变）
            scene_data = self._simulation_service.get_scene_data_for_gui()
            self.simulation_canvas.update_scene(scene_data)
    
    def _update_command_panel_options(self):
        """更新命令面板的选项数据"""
        # 更新任务模板
        templates = self._command_service.get_task_templates()
        self.command_panel.set_task_template_options(templates)
        
        # 更新任务ID列表
        task_ids = self._command_service.get_task_ids()
        self.command_panel.set_update_task_options(task_ids)
        
        # 更新命令选项
        commands = self._command_service.get_command_options()
        self.command_panel.set_update_command_options(commands)

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


    def get_user_command(self) -> str:
        """获取用户命令"""
        return self.command_panel.get_new_task_instruction()
    
    def send_user_command(self) -> bool:
        """发送用户命令到后端"""
        command_text = self.get_user_command()
        if command_text and command_text.strip():
            success = self._command_service.send_user_command(command_text)
            if success:
                self.command_panel.clear_new_task_instruction()
                # 刷新数据
                self.refresh_all_data()
            return success
        return False

    def _setShadowEffect(self, card: QWidget):
        shadowEffect = QGraphicsDropShadowEffect(self)
        shadowEffect.setColor(QColor(0, 0, 0, 0))
        shadowEffect.setBlurRadius(8)
        shadowEffect.setOffset(0, 0)
        card.setGraphicsEffect(shadowEffect)

    # def set_command_hint(self, text: str):
    #     self.command_panel.set_command_hint(text)
    
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 依赖注入：在__main__中创建backend并注入到HomeInterface
    # 这样可以灵活切换不同的后端实现（ExampleBackendAdapter, RestApiBackend, DatabaseBackend等）
    backend = ExampleBackendAdapter()
    home_interface = HomeInterface(backend=backend)
    home_interface.show()
    
    sys.exit(app.exec_())