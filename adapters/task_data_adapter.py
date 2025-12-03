"""
Task 数据适配器

将 MediatorService.fetch_task_data() 返回的标准格式数据
转换为 TaskInfoPanel 需要的展示格式。
"""
from typing import List, Dict, Any


class TaskDataAdapter:
    """Task 数据适配器，负责数据格式转换"""
    
    @staticmethod
    def convert_table_data(tasks: List[Dict]) -> List[List[str]]:
        """将任务数据转换为表格数据"""
        table_data = []
        for task in tasks:
            row = [
                str(task.get('id', 'N/A')),
                task.get('type', '未知'),
                task.get('area', 'N/A'),
                str(task.get('coalition_id', 'N/A')),
                TaskDataAdapter._format_task_status(task.get('status', 'unknown'))
            ]
            table_data.append(row)
        return table_data
    
    @staticmethod
    def convert_gantt_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """将任务数据转换为甘特图数据"""
        tasks = data.get('tasks', [])
        
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
                    "color": TaskDataAdapter._get_task_color(task.get('type', 'unknown')),
                    "text": f"T{task.get('id', 'N/A')}",
                    "alpha": 0.8
                })
            
            tracks.append({
                "label": f"Coalition-{coalition_id}" if coalition_id >= 0 else "Unassigned",
                "bars": sorted(bars, key=lambda x: x['start'])
            })
        
        return {
            "tracks": tracks,
            "current_time": data.get('current_time', 0),
            "y_label_fontsize": 10
        }
    
    @staticmethod
    def _format_task_status(status: str) -> str:
        """将中介服务任务状态转换为中文显示"""
        status_map = {
            'pending': '待执行',
            'executing': '执行中',
            'completed': '已完成',
            'failed': '失败',
            'cancelled': '已取消',
            'unknown': '未知'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def _get_task_color(task_type: str) -> str:
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

