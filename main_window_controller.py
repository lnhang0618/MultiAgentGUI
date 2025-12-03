"""
MainWindow 控制器（UI 协调层）

职责划分：
- UI 生命周期管理：创建、显示、隐藏、关闭 MainWindow
- UI 事件绑定：连接 UI 信号到 Mediator 方法
- UI 操作：文件对话框、UI 定时器等
- 数据刷新协调：定时从 Mediator 拉取数据并更新 UI
- 模板加载：从 Mediator 获取模板数据并设置到 UI

架构设计：
- Controller 管理 MainWindow（符合 MVC/MVP 模式）
- MainWindow 只负责 UI 组装，不依赖 Controller
- Controller 负责 UI 业务逻辑协调，不处理数据格式转换
- Mediator 负责后端适配和数据格式转换

职责边界（重要）：
┌─────────────────────────────────────────────────────────┐
│ Controller (UI 协调层)                                    │
│ ✅ 何时做什么：定时器管理、事件绑定时机                   │
│ ✅ UI 操作：文件对话框、窗口显示/隐藏                     │
│ ✅ 数据流转：从 Mediator 获取数据并传递给 UI              │
│ ❌ 不负责：数据格式转换、后端交互、业务逻辑处理           │
└─────────────────────────────────────────────────────────┘
                          ↓ 调用
┌─────────────────────────────────────────────────────────┐
│ Mediator (后端适配层)                                     │
│ ✅ 提供什么数据：从后端获取并转换为标准格式                │
│ ✅ 处理什么命令：将标准格式命令转换为后端格式              │
│ ✅ 后端交互：实际的后端通信和数据格式转换                 │
│ ❌ 不负责：UI 生命周期、UI 操作、定时器管理               │
└─────────────────────────────────────────────────────────┘
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Callable
from PyQt5.QtCore import QTimer

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

from MultiAgentGUI.services.mediator_service import MediatorService
from MultiAgentGUI.main_window import MainWindow


class MainWindowController:
    """
    MainWindow 控制器（UI 协调层）
    
    核心职责：
    1. UI 生命周期管理：创建、显示、隐藏、关闭 MainWindow
    2. UI 事件协调：连接 UI 信号到 Mediator 方法（不处理业务逻辑）
    3. UI 操作：文件对话框、定时器等 UI 相关操作
    4. 数据刷新协调：管理定时器，从 Mediator 拉取数据并传递给 UI
    
    不负责：
    - 数据格式转换（由 Mediator 负责）
    - 后端交互（由 Mediator 负责）
    - 业务逻辑处理（由 Mediator 负责）
    
    设计模式：MVP (Model-View-Presenter)
    - Controller 持有并管理 MainWindow（View）
    - MainWindow 是被动的，不持有 Controller 引用
    - View → Controller 通信通过信号/槽
    - Controller → View 通信通过直接方法调用
    """
    
    def __init__(self, mediator: Optional[MediatorService] = None, parent=None):
        """
        初始化控制器并创建 MainWindow
        
        参数：
            mediator: MediatorService 实例（可选）
            parent: MainWindow 的父窗口（可选）
        """
        self.mediator = mediator
        self._data_timer: Optional[QTimer] = None
        
        # 创建 MainWindow（由 Controller 管理，不传入 mediator）
        self.main_window = MainWindow(parent=parent)
        
        # 连接规划器选择事件到 Controller
        # 注意：_planner_panel 在 MainWindow.__init__ 中已初始化
        if hasattr(self.main_window, '_planner_panel'):
            self.main_window._planner_panel.planner_selected.connect(
                self.handle_planner_selection
            )
        
        # 如果提供了 mediator，进行绑定
        if self.mediator is not None:
            self.setup_bindings()
            self.start_data_refresh()
    
    def show(self):
        """显示主窗口"""
        self.main_window.show()
    
    def hide(self):
        """隐藏主窗口"""
        self.main_window.hide()
    
    def close(self):
        """关闭主窗口并清理资源"""
        self.stop_data_refresh()
        self.main_window.close()
    
    def setup_bindings(self):
        """
        设置所有数据绑定和事件转发（UI协调层）
        
        职责：
        - 连接 UI 信号到 Mediator 方法
        - 不处理数据格式转换（由 Mediator 负责）
        - 不处理后端操作（由 Mediator 负责）
        """
        if self.mediator is None:
            return
        
        # 绑定仿真视图和场景设计视图（数据绘制：Mediator负责）
        self._bind_simulation_views()
        
        # 绑定场景交互事件（事件转发：UI→Mediator）
        self._bind_scene_events()
        
        # 绑定工具栏事件（UI操作：Controller负责文件对话框）
        self._bind_toolbar_events()
        
        # 绑定命令面板事件（命令转发：UI→Mediator）
        self._bind_command_panel()
        
        # 加载模板数据（数据加载：从Mediator获取并设置到UI）
        self._load_templates()
        
        # 加载规划器选项（数据加载：从Mediator获取并设置到UI）
        self._load_planner_options()
        
        # 注册UI操作回调给Mediator（可选）
        self._register_ui_callbacks()
    
    def _bind_simulation_views(self):
        """
        绑定仿真视图和场景设计视图
        
        职责边界：
        - Controller：获取 Mediator 的绘制器并调用（协调）
        - Mediator：提供绘制器，实现后端特定的绘制逻辑（绘制策略）
        
        设计理念：
        - Mediator 不再直接操作 UI，而是提供绘制器接口
        - Controller 负责调用绘制器，但不知道具体绘制细节
        - 不同后端可以实现完全不同的绘制逻辑
        """
        if not self._check_mediator_method('get_canvas_renderer'):
            return
        
        try:
            renderer = self.mediator.get_canvas_renderer()
            if renderer is None:
                # Mediator 不支持绘制，这是正常的（可选功能）
                return
            
            # 获取画布组件
            sim_canvas = self.main_window.sim_panel.get_canvas()
            design_canvas = self.main_window.sim_scenario_panel.get_canvas()
            
            if sim_canvas is None or design_canvas is None:
                self._log_error("获取画布", Exception("画布组件为 None"))
                return
            
            # 获取初始场景数据
            if hasattr(self.mediator, 'fetch_simulation_scene'):
                scene_data = self.mediator.fetch_simulation_scene()
            else:
                scene_data = {}
            
            # 使用绘制器渲染初始场景
            renderer.render_initial_scene(sim_canvas, scene_data)
            renderer.render_initial_scene(design_canvas, scene_data)
            
        except Exception as e:
            self._log_error("绑定仿真视图", e)
    
    def _bind_scene_events(self):
        """
        绑定场景交互事件
        
        职责边界：
        - Controller：转发 UI 事件信号到 Mediator（协调）
        - Mediator：处理事件、修改后端数据、刷新显示（业务逻辑）
        """
        if not self._check_mediator_method('handle_design_scene_event'):
            return
        
        # 场景设计面板的编辑事件
        try:
            self.main_window.sim_scenario_panel.scene_edit_requested.connect(
                self.mediator.handle_design_scene_event
            )
        except Exception as e:
            self._log_error("连接 scene_edit_requested", e)
        
        # 仿真视图的交互事件
        try:
            self.main_window.sim_panel.scene_interaction.connect(
                self.mediator.handle_design_scene_event
            )
        except Exception as e:
            self._log_error("连接 scene_interaction", e)
    
    def _bind_toolbar_events(self):
        """
        绑定工具栏事件
        
        职责边界：
        - Controller：处理 UI 操作（文件对话框）
        - Mediator：处理数据（文件加载、数据更新）
        """
        # 导入背景图
        try:
            self.main_window.sim_scenario_panel.import_background_requested.connect(
                self._handle_import_background_request
            )
        except Exception as e:
            self._log_error("连接 import_background_requested", e)
        
        # 导入矢量图
        try:
            self.main_window.sim_scenario_panel.import_vector_requested.connect(
                self._handle_import_vector_request
            )
        except Exception as e:
            self._log_error("连接 import_vector_requested", e)
    
    def _handle_import_background_request(self):
        """
        处理导入背景图请求
        
        职责边界：
        - Controller：打开文件对话框（UI 操作）
        - Mediator：加载文件、更新数据（数据处理）
        """
        if self.mediator is None:
            return
        
        # Controller 负责：UI 操作（文件对话框）
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "选择背景图",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)"
        )
        
        if file_path:
            # Controller 负责：将文件路径传递给 Mediator 处理
            if self._check_mediator_method('import_background_file'):
                try:
                    self.mediator.import_background_file(file_path)
                except Exception as e:
                    self._log_error("导入背景图", e)
    
    def _handle_import_vector_request(self):
        """
        处理导入矢量图请求
        
        职责边界：
        - Controller：打开文件对话框（UI 操作）
        - Mediator：加载文件、更新数据（数据处理）
        """
        if self.mediator is None:
            return
        
        # Controller 负责：UI 操作（文件对话框）
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "选择矢量图",
            "",
            "矢量图文件 (*.svg *.dxf);;所有文件 (*)"
        )
        
        if file_path:
            # Controller 负责：将文件路径传递给 Mediator 处理
            if self._check_mediator_method('import_vector_file'):
                try:
                    self.mediator.import_vector_file(file_path)
                except Exception as e:
                    self._log_error("导入矢量图", e)
    
    def _bind_command_panel(self):
        """
        绑定命令面板的命令发送事件
        
        职责边界：
        - Controller：转发 UI 命令信号到 Mediator（协调）
        - Mediator：将标准格式命令转换为后端格式并发送（业务逻辑）
        """
        if not self._check_mediator_method('receive_command', required=True):
            return
        
        try:
            self.main_window.command_panel.command_sent.connect(
                self.mediator.receive_command
            )
        except Exception as e:
            self._log_error("连接 command_sent", e)
    
    def _load_templates(self):
        """
        加载任务模板到命令面板
        
        职责边界：
        - Controller：从 Mediator 获取数据并设置到 UI（协调）
        - Mediator：提供模板数据（数据提供）
        """
        if self.mediator is None:
            return
        
        if not self._check_mediator_method('get_task_templates'):
            return
        
        try:
            templates = self.mediator.get_task_templates()
            self.main_window.command_panel.set_publish_templates(templates)
            # 修改指令模板暂时使用相同的模板列表
            self.main_window.command_panel.set_modify_templates(templates)
        except Exception as e:
            self._log_error("加载任务模板", e)
    
    def _load_planner_options(self):
        """
        加载规划器选项
        
        职责边界：
        - Controller：从 Mediator 获取数据并设置到 UI（协调）
        - Mediator：提供规划器选项数据（数据提供）
        """
        if self.mediator is None:
            return
        
        # 确保 planner_panel 已初始化
        if not hasattr(self.main_window, '_planner_panel'):
            return
        
        if not self._check_mediator_method('get_planner_options'):
            return
        
        try:
            red_planners, blue_planners = self.mediator.get_planner_options()
            self.main_window._planner_panel.set_planner_options(red_planners, blue_planners)
        except Exception as e:
            self._log_error("加载规划器选项", e)
    
    def start_data_refresh(self, interval: int = 1000):
        """
        启动定时器，周期性从 mediator 拉取数据并刷新面板
        
        职责边界：
        - Controller：管理 UI 定时器，定时触发数据刷新（协调）
        - Mediator：提供标准格式数据（数据提供）
        - Controller：将标准格式数据传递给 UI 显示（协调）
        
        参数：
            interval: 刷新间隔（毫秒），默认 1000ms
        """
        if self.mediator is None:
            return
        
        self._data_timer = QTimer(self.main_window)
        self._data_timer.setInterval(interval)
        self._data_timer.timeout.connect(self._refresh_panels)
        self._data_timer.start()
    
    def stop_data_refresh(self):
        """停止数据刷新定时器"""
        if self._data_timer is not None:
            self._data_timer.stop()
            self._data_timer = None
    
    def _refresh_panels(self):
        """
        从 mediator 获取最新数据并刷新各个信息面板
        
        职责边界：
        - Controller：从 Mediator 拉取标准格式数据并传递给 UI（协调）
        - Mediator：从后端获取数据并转换为标准格式（数据适配）
        - Panel：接收标准格式数据并显示（UI展示）
        """
        if self.mediator is None:
            return
        
        # 刷新 Agent 信息（必需方法）
        if self._check_mediator_method('fetch_agent_data'):
            try:
                agent_data = self.mediator.fetch_agent_data()
                self.main_window.agent_panel.load_data(agent_data)
            except Exception as e:
                self._log_error("刷新 Agent 数据", e)
        
        # 刷新 Task 信息（必需方法）
        if self._check_mediator_method('fetch_task_data'):
            try:
                task_data = self.mediator.fetch_task_data()
                # get_task_graph_data 是可选方法
                graph_data = None
                if self._check_mediator_method('get_task_graph_data'):
                    try:
                        graph_data = self.mediator.get_task_graph_data()
                    except Exception as e:
                        self._log_error("获取任务图数据", e)
                
                self.main_window.task_panel.load_data(task_data, graph_data)
            except Exception as e:
                self._log_error("刷新 Task 数据", e)
    
    def handle_planner_selection(self, faction: str, planner_name: str):
        """
        处理规划器选择变化
        
        职责边界：
        - Controller：转发 UI 选择事件到 Mediator（协调）
        - Mediator：更新后端规划器配置（命令处理）
        """
        if self.mediator is None:
            return
        
        if self._check_mediator_method('handle_planner_selection'):
            try:
                self.mediator.handle_planner_selection(faction, planner_name)
            except Exception as e:
                self._log_error("处理规划器选择", e)
    
    def _show_notification(self, message: str, notification_type: str = "info", duration: int = 3000):
        """
        显示浮窗通知（UI操作实现）
        
        参数：
            message: 通知消息内容
            notification_type: 通知类型 ("info", "success", "warning", "error")
            duration: 显示时长（毫秒），默认3000ms
        """
        try:
            from qfluentwidgets import InfoBar, InfoBarPosition, InfoBarIcon
            from PyQt5.QtCore import Qt
            
            icon_map = {
                "info": InfoBarIcon.INFORMATION,
                "success": InfoBarIcon.SUCCESS,
                "warning": InfoBarIcon.WARNING,
                "error": InfoBarIcon.ERROR,
            }
            
            InfoBar.new(
                icon=icon_map.get(notification_type, InfoBarIcon.INFORMATION),
                title="提示",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=self.main_window
            )
        except Exception as e:
            print(f"[MainWindowController] 显示浮窗通知失败: {e}")
    
    def _get_ui_callbacks(self) -> Dict[str, Callable]:
        """
        获取UI操作回调函数字典
        
        定义后端可以请求的UI操作类型和对应的处理函数
        
        返回：回调函数字典，键为操作名称，值为回调函数
        """
        return {
            'show_notification': self._show_notification,
            # 未来可以扩展其他UI操作：
            # 'show_dialog': self._show_dialog,
            # 'update_status_bar': self._update_status_bar,
            # 'highlight_panel': self._highlight_panel,
        }
    
    def _register_ui_callbacks(self):
        """
        向 Mediator 注册 UI 操作回调（可选）
        
        职责边界：
        - Controller：提供 UI 操作回调函数给 Mediator（协调）
        - Mediator：可以在需要时调用这些回调来触发 UI 操作（反馈）
        
        注意：这是反向通信机制，允许 Mediator 主动触发 UI 操作（如显示通知）
        """
        if self.mediator is None:
            return
        
        if self._check_mediator_method('set_ui_callbacks'):
            try:
                callbacks = self._get_ui_callbacks()
                self.mediator.set_ui_callbacks(callbacks)
                print("[MainWindowController] UI操作回调已注册")
            except Exception as e:
                self._log_error("注册UI回调", e)
    
    # ---------- 辅助方法：统一错误处理和检查 ----------
    
    def _check_mediator_method(self, method_name: str, required: bool = False) -> bool:
        """
        检查 Mediator 是否实现了指定方法
        
        参数：
            method_name: 方法名称
            required: 是否为必需方法（如果是必需但未实现，会打印警告）
        
        返回：方法是否存在
        """
        if self.mediator is None:
            return False
        
        has_method = hasattr(self.mediator, method_name)
        if not has_method and required:
            print(f"[MainWindowController] 警告: mediator 未实现必需方法 '{method_name}'")
        return has_method
    
    def _log_error(self, operation: str, error: Exception) -> None:
        """
        统一错误日志记录
        
        参数：
            operation: 操作描述
            error: 异常对象
        """
        print(f"[MainWindowController] {operation} 失败: {error}")


if __name__ == "__main__":
    """
    应用入口
    
    从架构角度看，应用入口应该放在 Controller 中，因为：
    - Controller 是应用的协调者，负责管理整个应用的生命周期
    - MainWindow 作为 View 层，不应该包含应用启动逻辑
    - 这样更符合 MVC/MVP 模式的设计原则
    """
    import sys
    from PyQt5.QtWidgets import QApplication
    from MultiAgentGUI.example_mediator_service import ExampleMediatorService

    app = QApplication(sys.argv)
    mediator = ExampleMediatorService()
    # 使用 Controller 管理 MainWindow
    controller = MainWindowController(mediator=mediator)
    controller.show()
    sys.exit(app.exec_())

