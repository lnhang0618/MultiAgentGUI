# services/task_service.py
from typing import List, Tuple, Dict, Any
from .backend_adapter import BackendAdapter


class TaskService:
    """
    Task服务层
    具体部分：GUI接口格式转换（写死）
    抽象部分：后端数据获取（委托给BackendAdapter）
    """
    
    def __init__(self, backend: BackendAdapter):
        """
        参数：
            backend: 后端适配器实例
        """
        self._backend = backend
    
    def get_task_data_for_gui(self) -> Tuple[List[List[str]], Dict[str, Any], str]:
        """
        获取任务数据，转换为GUI需要的格式
        返回：(table_data, gantt_data, ltl_text)
            - table_data: List[List[str]] - 表格数据
            - gantt_data: Dict - 甘特图数据
            - ltl_text: str - LTL公式文本
        """
        raw_data = self._backend.fetch_task_data()
        
        # 转换表格数据
        table_data = self._convert_to_table_data(raw_data)
        
        # 转换甘特图数据
        gantt_data = self._convert_to_gantt_data(raw_data)
        
        # 获取LTL公式
        ltl_text = raw_data.get('ltl_formula', '暂无LTL公式')
        
        return table_data, gantt_data, ltl_text
    
    def _convert_to_table_data(self, raw_data: Dict[str, Any]) -> List[List[str]]:
        """
        将后端任务数据转换为表格数据
        GUI需求：[['序号', '任务类型', '区域', '子群', '状态'], ...]
        """
        tasks = raw_data.get('tasks', [])
        table_data = []
        
        for task in tasks:
            row = [
                str(task.get('id', 'N/A')),
                task.get('type', '未知'),
                task.get('area', 'N/A'),
                str(task.get('coalition_id', 'N/A')),
                self._format_task_status(task.get('status', 'unknown'))
            ]
            table_data.append(row)
        
        return table_data
    
    def _convert_to_gantt_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将后端任务数据转换为甘特图数据
        GUI需求：{
            "tracks": [{"label": "...", "bars": [...]}],
            "current_time": ...
        }
        """
        tasks = raw_data.get('tasks', [])
        
        # 按子群分组任务
        coalition_tasks = {}
        for task in tasks:
            cid = task.get('coalition_id', -1)
            if cid not in coalition_tasks:
                coalition_tasks[cid] = []
            coalition_tasks[cid].append(task)
        
        # 生成甘特图轨道
        tracks = []
        for coalition_id, task_list in coalition_tasks.items():
            bars = []
            for task in task_list:
                bars.append({
                    "start": task.get('start_time', 0),
                    "duration": task.get('duration', 0),
                    "color": self._get_task_color(task.get('type', 'unknown')),
                    "text": f"T{task.get('id', 'N/A')}",
                    "alpha": 0.8
                })
            
            tracks.append({
                "label": f"Coalition-{coalition_id}" if coalition_id >= 0 else "Unassigned",
                "bars": sorted(bars, key=lambda x: x['start'])
            })
        
        return {
            "tracks": tracks,
            "current_time": raw_data.get('current_time', 0),
            "y_label_fontsize": 10
        }
    
    def _format_task_status(self, status: str) -> str:
        """将后端任务状态转换为中文显示"""
        status_map = {
            'pending': '待执行',
            'executing': '执行中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消',
            'unknown': '未知'
        }
        return status_map.get(status, status)
    
    def _get_task_color(self, task_type: str) -> str:
        """根据任务类型返回颜色"""
        color_map = {
            'patrol': 'lightblue',
            'surveillance': 'lightgreen',
            'search': 'lightyellow',
            'rescue': 'lightcoral',
            'transport': 'lightpink',
            'unknown': 'gray'
        }
        return color_map.get(task_type, 'silver')

