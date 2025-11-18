# services/command_service.py
from typing import List, Dict, Any
from .backend_adapter import BackendAdapter


class CommandService:
    """
    Command服务层
    具体部分：GUI指令解析和格式转换（写死）
    抽象部分：后端命令发送（委托给BackendAdapter）
    """
    
    def __init__(self, backend: BackendAdapter):
        """
        参数：
            backend: 后端适配器实例
        """
        self._backend = backend
    
    def send_user_command(self, instruction_text: str) -> bool:
        """
        发送用户指令到后端
        参数：
            instruction_text: GUI输入的纯文本指令
        返回：是否发送成功
        """
        # 具体实现：将GUI文本转换为标准命令格式
        command_data = self._parse_instruction(instruction_text)
        
        # 抽象调用：委托给后端适配器
        return self._backend.send_command(command_data)
    
    def get_task_templates(self) -> List[str]:
        """
        获取任务模板列表
        返回：模板名称列表
        """
        return self._backend.get_task_templates()
    
    def get_task_ids(self) -> List[str]:
        """
        获取当前任务ID列表
        返回：任务ID字符串列表
        """
        return self._backend.get_task_ids()
    
    def get_command_options(self) -> List[str]:
        """
        获取可用的命令选项列表
        返回：命令选项字符串列表
        """
        return self._backend.get_command_options()
    
    def _parse_instruction(self, text: str) -> Dict[str, Any]:
        """
        将GUI文本指令转换为标准命令格式
        具体实现：根据GUI需求解析指令
        """
        import datetime
        
        # 简单的指令解析（实际可以更复杂）
        command_type = "user_command"
        
        # 尝试识别指令类型
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['开始', 'start', '执行', 'execute']):
            command_type = "start"
        elif any(keyword in text_lower for keyword in ['停止', 'stop', '暂停', 'pause']):
            command_type = "stop"
        elif any(keyword in text_lower for keyword in ['更新', 'update', '修改', 'modify']):
            command_type = "update"
        elif any(keyword in text_lower for keyword in ['删除', 'delete', '移除', 'remove']):
            command_type = "delete"
        
        return {
            "type": command_type,
            "instruction": text,
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "gui"
        }

