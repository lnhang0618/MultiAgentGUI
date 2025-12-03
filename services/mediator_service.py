# services/mediator_service.py
"""
中介服务接口规范

将后端适配器分为两个独立的接口模块，实现职责分离和数据隔离：
1. DataProvider（数据提供者）：负责从后端获取数据（后端→UI）
2. CommandHandler（命令处理器）：负责处理UI的命令（UI→后端）

MediatorService同时实现这两个接口，作为统一的中介服务。

此外，还支持可选的绘制器接口（CanvasRenderer）：
- Mediator 可以实现绘制器接口，封装后端特定的绘制逻辑
- Controller 获取绘制器并调用，但不知道具体绘制细节
- 这样既保持了职责分离，又允许后端特定的绘制逻辑
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Any as TypingAny, Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from MultiAgentGUI.services.canvas_renderer import CanvasRenderer


class DataProvider(ABC):
    """
    数据提供者接口（后端→UI）
    
    负责从后端获取数据并转换为标准格式。
    所有数据获取相关的方法都在此接口中定义。
    """
    
    @abstractmethod
    def fetch_agent_data(self) -> Dict[str, Any]:
        """
        获取Agent相关数据（子群、无人机等）
        
        返回：适配后的标准格式字典，包含以下字段：
        {
            'coalitions': [
                {
                    'id': int,                    # 子群ID
                    'current_task': str,          # 当前任务名称
                    'members': List[int],         # 成员ID列表
                    'schedule': [                 # 任务日程
                        {'start': float, 'end': float, 'task': str, 'color': str},
                        ...
                    ],
                    'replan_schedule': [...]      # 重规划日程（可选）
                },
                ...
            ],
            'agents': [
                {
                    'id': int,                    # 智能体ID
                    'type': str,                  # 类型（如'侦察型无人机'）
                    'coalition_id': int | None,   # 所属子群ID（敌方可能为None）
                    'status': str,                # 状态（'idle', 'working', 'charging'等）
                    'faction': str,               # 阵营（'红军'/'蓝军'）
                    'x': float,                   # X坐标
                    'y': float                    # Y坐标
                },
                ...
            ],
            'current_time': float                 # 当前时间戳
        }
        
        注意：作为适配器，此方法应将后端原始数据转换为上述标准格式。
        不同后端可能有不同的原始格式，但都应统一转换为该标准格式。
        """
        pass
    
    @abstractmethod
    def fetch_task_data(self) -> Dict[str, Any]:
        """
        获取Task相关数据
        
        返回：适配后的标准格式字典，包含以下字段：
        {
            'tasks': [
                {
                    'id': int,                    # 任务ID
                    'type': str,                  # 任务类型（如'patrol', 'surveillance'）
                    'area': str,                  # 任务区域
                    'coalition_id': int | -1,     # 所属子群ID（-1表示未分配）
                    'status': str,                # 状态（'executing', 'pending'等）
                    'start_time': float,          # 开始时间
                    'duration': float,            # 持续时间
                    'ltl': str                    # LTL公式
                },
                ...
            ],
            'ltl_formula': str,                  # 所有任务的组合LTL公式
            'current_time': float                 # 当前时间戳
        }
        
        注意：作为适配器，此方法应将后端原始数据转换为上述标准格式。
        不同后端可能有不同的原始格式，但都应统一转换为该标准格式。
        """
        pass
    
    @abstractmethod
    def fetch_simulation_scene(self, timestamp: float = None) -> Dict[str, Any]:
        """
        获取仿真场景数据
        
        参数：
            timestamp: 时间戳，None表示当前时间（可用于回放历史数据）
        
        返回：适配后的标准格式字典，包含以下字段：
        {
            'agents': [
                {
                    'id': int,                    # 智能体ID
                    'x': float,                   # X坐标
                    'y': float,                   # Y坐标
                    'color': str,                 # 颜色（十六进制，如'#FF0000'）
                    'symbol': str                 # 符号（'o', 's', 't', 'd', '+'等）
                },
                ...
            ],
            'targets': [
                {
                    'x': float,                   # X坐标
                    'y': float,                   # Y坐标
                    'color': str,                 # 颜色
                    'active': bool                # 是否激活
                },
                ...
            ],
            'regions': [
                {
                    'type': str,                  # 类型（'circle'或'polygon'）
                    'color': str,                 # 颜色
                    'center': tuple,              # 圆心（circle类型）
                    'radius': float,              # 半径（circle类型）
                    'points': List[tuple]         # 顶点列表（polygon类型）
                },
                ...
            ],
            'trajectories': [
                {
                    'points': List[List[float]],  # 轨迹点列表 [[x1,y1], [x2,y2], ...]
                    'color': str                  # 轨迹颜色
                },
                ...
            ],
            'time': float,                        # 当前时间戳
            'limits': {
                'x_min': float,                   # X轴最小值
                'x_max': float,                   # X轴最大值
                'y_min': float,                   # Y轴最小值
                'y_max': float                    # Y轴最大值
            }
        }
        
        注意：作为适配器，此方法应将后端原始数据转换为上述标准格式。
        不同后端可能有不同的原始格式，但都应统一转换为该标准格式。
        """
        pass
    
    @abstractmethod
    def get_task_templates(self) -> List[str]:
        """
        获取任务模板列表
        返回：模板名称列表
        """
        pass
    
    def get_task_template_content(self, template_name: str) -> str:
        """
        获取任务模板的详细内容（instruction文本）
        
        参数：
            template_name: 模板名称
        
        返回：模板的instruction文本内容
        
        注意：这是一个可选方法，如果后端不支持获取模板内容，可以返回模板名称本身
        """
        # 默认实现：返回模板名称（子类可以覆盖此方法提供实际内容）
        return template_name
    
    def get_task_graph_data(self) -> Dict[str, Any]:
        """
        获取任务图数据（任务之间的逻辑依赖关系）
        
        返回：标准化的任务图数据字典，包含以下字段：
        {
            'nodes': [
                {
                    'id': str | int,              # 节点ID（唯一标识，通常对应任务ID）
                    'label': str                 # 节点标签（显示文本，如任务名称）
                },
                ...
            ],
            'edges': [
                {
                    'source': str | int,           # 源节点ID
                    'target': str | int,          # 目标节点ID
                    'type': str                    # 边类型："sequence"（先后顺序，有箭头）或 "parallel"（同时关系，无箭头虚线），默认"sequence"
                },
                ...
            ],
            'layout': {                           # 布局配置（可选）
                'algorithm': str                  # 布局算法（'spring'/'circular'/'hierarchical'，默认'spring'）
            }
        }
        
        注意：
        - 这是一个可选方法，如果后端不支持任务图，可以返回空数据
        - 任务图表示任务之间的逻辑依赖关系，不涉及coalition信息
        - UI使用简单的圆形节点展示关系：
          * 先后顺序关系（type="sequence"）：有箭头的实线
          * 同时关系（type="parallel"）：无箭头的虚线
        - 作为适配器，此方法应将后端原始数据转换为上述标准格式
        """
        # 默认实现：返回空数据（子类可以覆盖此方法提供实际数据）
        return {
            'nodes': [],
            'edges': [],
            'layout': {'algorithm': 'spring'}
        }
    
    @abstractmethod
    def get_task_ids(self) -> List[str]:
        """
        获取当前任务ID列表
        返回：任务ID字符串列表
        """
        pass
    
    @abstractmethod
    def get_command_options(self) -> List[str]:
        """
        获取可用的命令选项列表
        返回：命令选项字符串列表
        """
        pass

    def get_available_planners(self) -> List[Dict[str, str]]:
        """
        获取可供 GUI 启动的 planner 列表
        返回：[{key,label,description}, ...]
        """
        return []

    def get_simulation_status(self) -> str:
        """
        获取当前仿真状态：idle/running/paused/stopped/unknown
        """
        return "unknown"
    
    def is_simulation_running(self) -> bool:
        """
        检查仿真是否正在运行
        返回：True表示仿真正在运行，False表示已停止
        
        注意：这是一个可选方法，如果后端不支持仿真控制，可以返回False
        """
        return False
    
    def step_simulation(self) -> bool:
        """
        推进仿真一个时间步
        返回：是否成功推进
        
        注意：
        - 这是一个可选方法，如果后端不支持时间步控制，可以返回False
        - 时间步长由后端自己决定（固定步长、自适应步长等）
        - 前端只负责触发，不关心具体的时间步长
        """
        return False
    
    def get_current_time(self) -> float:
        """
        获取当前仿真时间
        返回：当前时间戳（秒）
        
        注意：这是一个可选方法，用于显示当前时间
        """
        return 0.0


class CommandHandler(ABC):
    """
    命令处理器接口（UI→后端）
    
    负责接收UI的命令并发送到后端。
    所有命令处理相关的方法都在此接口中定义。
    """
    
    @abstractmethod
    def receive_command(self, command_data: Dict[str, Any]) -> bool:
        """
        接收UI的命令并发送到后端
        
        参数：
            command_data: 标准化的命令数据字典，可能包含以下格式：
            
            1. 创建任务 (type="create_task"):
            {
                "type": "create_task",
                "instruction": str,          # 任务指令文本
                "template": str | None,      # 任务模板名称（可选）
                "timestamp": str,            # ISO格式时间戳
                "source": "gui"
            }
            
            2. 修改任务 (type="update_task"):
            {
                "type": "update_task",
                "task_id": str,              # 任务ID
                "command": str,              # 命令选项（如"暂停任务"、"恢复任务"等）
                "timestamp": str,
                "source": "gui"
            }
            
            3. 任务重规划 (type="replan"):
            {
                "type": "replan",
                "timestamp": str,
                "source": "gui"
            }
            
            4. 开始仿真 (type="start_simulation"):
            {
                "type": "start_simulation",
                "timestamp": str,
                "source": "gui"
            }
            
            5. 通用用户指令 (type="user_command" 或其他):
            {
                "type": str,                 # 命令类型
                "instruction": str,          # 指令文本
                "timestamp": str,
                "source": "gui"
            }
        
        返回：是否接收并发送成功
        
        注意：
        - 此方法从UI的角度看是"接收命令"，从后端角度看是"发送命令"
        - 作为适配器，此方法应将标准化的命令数据转换为后端需要的格式并发送
        - 不同后端可能有不同的命令格式，但都应接收上述标准格式
        """
        pass


class MediatorService(DataProvider, CommandHandler):
    """
    中介服务接口（后端适配层）
    
    同时实现 DataProvider 和 CommandHandler 接口，作为统一的中介服务。
    后端适配器应该继承此类并实现所有抽象方法。
    
    核心职责：
    1. 数据提供（DataProvider）：从后端获取数据并转换为标准格式（后端→UI）
    2. 命令处理（CommandHandler）：接收标准格式命令并转换为后端格式（UI→后端）
    3. 后端适配：适配不同后端的数据格式和通信协议
    
    职责边界（重要）：
    ┌─────────────────────────────────────────────────────────┐
    │ Mediator (后端适配层)                                     │
    │ ✅ 提供什么数据：从后端获取并转换为标准格式              │
    │ ✅ 处理什么命令：将标准格式命令转换为后端格式            │
    │ ✅ 后端交互：实际的后端通信和数据格式转换                │
    │ ❌ 不负责：UI 生命周期、UI 操作、定时器管理               │
    └─────────────────────────────────────────────────────────┘
    
    设计理念：
    - DataProvider：负责数据获取（后端→UI），数据流单向
    - CommandHandler：负责命令处理（UI→后端），数据流单向
    - 两个接口完全隔离，互不干扰，便于维护和扩展
    
    可选功能：
    - 与前端画布的轻量交互（数据绘制层）
    - UI 操作回调机制（反向通信，用于反馈操作结果）
    """
    
    def __init__(self):
        """初始化MediatorService"""
        # UI操作回调函数字典（可选）
        # Controller 通过 set_ui_callbacks() 注册回调
        self._ui_callbacks: Optional[Dict[str, Callable]] = None

    # ---------- 可选：绘制器接口（Canvas Renderer） ----------
    def get_canvas_renderer(self) -> Optional['CanvasRenderer']:
        """
        获取画布绘制器（Canvas Renderer）
        
        职责说明：
        - Mediator 实现绘制器接口，封装后端特定的绘制逻辑
        - Controller 获取绘制器并调用，但不知道具体绘制细节
        - 不同后端可以实现完全不同的绘制逻辑
        
        返回：
            CanvasRenderer 实例，如果 Mediator 不支持绘制则返回 None
        
        设计理念：
        - Mediator 不直接操作 UI，而是提供绘制策略
        - Controller 负责协调绘制，但不知道具体绘制细节
        - 这样既保持了职责分离，又允许后端特定的绘制逻辑
        
        默认实现返回 None，具体中介服务可以覆盖此方法返回自定义的绘制器。
        """
        return None

    def handle_design_scene_event(self, event: Dict[str, TypingAny]) -> None:
        """
        处理来自场景视图的交互 / 编辑事件（事件处理层：UI→后端）。
        
        职责说明：
        - 此方法属于命令处理的一部分，负责将UI事件转换为后端操作
        - Controller 负责将UI信号转发到此方法
        - Mediator 负责根据事件修改后端数据并刷新显示
        
        event 的结构由前端约定，通常至少包含：
        - "source": "design" | "view"        # 来自场景设计面板或仿真结果面板
        - "type": "mouse_press" | "mouse_double_click" | "wheel" 等
        - "scene_pos": (x, y)                # 以场景坐标表示的点击/滚轮位置
        - 其他字段：如 "button"、"hit_count"、"delta"、"modifiers" 等

        默认实现不做任何事，具体中介服务可以覆盖此方法，根据事件修改后端场景数据，
        然后通过重新绘制的方式反馈到前端。
        """
        return
    
    def import_background_file(self, file_path: str) -> None:
        """
        导入背景图文件（数据处理层）。
        
        注意：此方法只负责数据处理，不包含UI操作（如文件对话框）。
        UI操作（文件选择）应由Controller负责。
        
        参数：
            file_path: 背景图文件路径
        
        默认实现不做任何事，具体中介服务可以覆盖此方法，例如：
        - 加载图片文件
        - 更新后端场景数据
        - 刷新画布显示
        """
        return
    
    def import_vector_file(self, file_path: str) -> None:
        """
        导入矢量图文件（数据处理层）。
        
        注意：此方法只负责数据处理，不包含UI操作（如文件对话框）。
        UI操作（文件选择）应由Controller负责。
        
        参数：
            file_path: 矢量图文件路径（SVG、DXF等）
        
        默认实现不做任何事，具体中介服务可以覆盖此方法，例如：
        - 加载矢量图文件
        - 更新后端场景数据
        - 在场景中添加矢量元素
        - 刷新画布显示
        """
        return
    
    def handle_planner_selection(self, faction: str, planner_name: str) -> None:
        """
        处理规划器选择变化（命令处理层：UI→后端）。
        
        职责说明：
        - 此方法属于命令处理的一部分，负责将UI选择转换为后端配置更新
        - Controller 负责将UI信号转发到此方法
        - Mediator 负责更新后端规划器配置

        参数:
            faction: "red" 或 "blue"，表示红方或蓝方
            planner_name: 选择的规划器名称
        
        默认实现不做任何事，具体中介服务可以覆盖此方法，例如：
        - 更新后端规划器配置
        - 重新加载规划器
        """
        return
    
    def get_planner_options(self) -> tuple:
        """
        获取可用的规划器选项。
        
        返回:
            (red_planners, blue_planners) 元组，每个都是字符串列表
            例如: (["规划器A", "规划器B"], ["规划器C", "规划器D"])
        
        默认实现返回空列表，具体中介服务可以覆盖此方法。
        """
        return ([], [])
    
    # ---------- 可选：UI操作回调机制 ----------
    def set_ui_callbacks(self, callbacks: Dict[str, Callable]) -> None:
        """
        设置UI操作回调函数（可选方法）。
        
        参数：
            callbacks: 回调函数字典，键为操作名称，值为回调函数
            例如：
            {
                'show_notification': callable(message, notification_type, duration),
                # 未来可以扩展其他操作：
                # 'show_dialog': callable(title, message, buttons),
                # 'update_status_bar': callable(message),
            }
        
        注意：
        - 此方法为可选，如果Mediator不需要UI操作回调，可以不实现
        - Controller 负责在 setup_bindings() 中调用此方法注册回调
        - Mediator 可以在处理命令时调用这些回调来触发UI操作
        - 回调函数的参数格式由Controller定义，Mediator需要按照格式调用
        
        使用示例：
        ```python
        # 在 Mediator 中调用UI回调
        self._call_ui_callback(
            'show_notification',
            message="命令执行成功，但需要注意资源限制",
            notification_type="warning",
            duration=5000
        )
        ```
        """
        self._ui_callbacks = callbacks
    
    def _call_ui_callback(self, callback_name: str, *args, **kwargs) -> Any:
        """
        调用UI操作回调（内部辅助方法）。
        
        参数：
            callback_name: 回调函数名称（如 'show_notification'）
            *args, **kwargs: 传递给回调函数的参数
        
        返回：回调函数的返回值，如果回调不存在则返回None
        
        注意：
        - 此方法用于Mediator内部调用UI回调
        - 调用前会检查回调是否存在，避免错误
        - 如果回调调用失败，会打印错误日志但不会抛出异常
        """
        if self._ui_callbacks and callback_name in self._ui_callbacks:
            try:
                callback = self._ui_callbacks[callback_name]
                return callback(*args, **kwargs)
            except Exception as e:
                print(f"[MediatorService] 调用UI回调 '{callback_name}' 失败: {e}")
        elif self._ui_callbacks is None:
            # 回调未注册，这是正常的（可选功能）
            pass
        else:
            # 回调已注册但指定的回调不存在
            print(f"[MediatorService] UI回调 '{callback_name}' 不存在")
        return None


