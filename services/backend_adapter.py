# services/backend_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BackendAdapter(ABC):
    """
    后端适配器抽象基类
    定义所有后端必须实现的接口，用于获取和发送数据
    """
    
    @abstractmethod
    def fetch_agent_data(self) -> Dict[str, Any]:
        """
        获取Agent相关数据（子群、无人机等）
        返回：后端原始格式的字典
        """
        pass
    
    @abstractmethod
    def fetch_task_data(self) -> Dict[str, Any]:
        """
        获取Task相关数据
        返回：后端原始格式的字典
        """
        pass
    
    @abstractmethod
    def fetch_simulation_scene(self, timestamp: float = None) -> Dict[str, Any]:
        """
        获取仿真场景数据
        参数：
            timestamp: 时间戳，None表示当前时间
        返回：场景原始数据
        """
        pass
    
    @abstractmethod
    def send_command(self, command_data: Dict[str, Any]) -> bool:
        """
        向后端发送命令
        参数：
            command_data: 标准化的命令数据字典
        返回：是否发送成功
        """
        pass
    
    @abstractmethod
    def get_task_templates(self) -> List[str]:
        """
        获取任务模板列表
        返回：模板名称列表
        """
        pass
    
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


