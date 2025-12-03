"""
数据适配器层

负责将 MediatorService 返回的标准格式数据转换为各个 Panel 需要的展示格式。
这样 Panel 只负责 UI 展示，不包含数据转换逻辑。
"""

from .agent_data_adapter import AgentDataAdapter
from .task_data_adapter import TaskDataAdapter

__all__ = [
    "AgentDataAdapter",
    "TaskDataAdapter",
]

