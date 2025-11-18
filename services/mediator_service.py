# services/mediator_service.py
"""
中介服务接口规范

将后端适配器分为两个独立的接口模块，实现职责分离和数据隔离：
1. DataProvider（数据提供者）：负责从后端获取数据（后端→UI）
2. CommandHandler（命令处理器）：负责处理UI的命令（UI→后端）

MediatorService同时实现这两个接口，作为统一的中介服务。
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


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
    中介服务接口
    
    同时实现DataProvider和CommandHandler接口，作为统一的中介服务。
    后端适配器应该继承此类并实现所有抽象方法。
    
    设计理念：
    - DataProvider：负责数据获取（后端→UI），数据流单向
    - CommandHandler：负责命令处理（UI→后端），数据流单向
    - 两个接口完全隔离，互不干扰，便于维护和扩展
    """
    pass

