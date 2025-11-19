# panels/task_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from typing import List, Tuple, Dict, Any
from components.navi_panel import NavigationPanel
from components.generic_tablewidget import GenericTableWidget
from components.generic_ganntwidget import GenericGanttChart
from components.generic_taskgraphwidget import GenericTaskGraphWidget
from qfluentwidgets import BodyLabel


class TaskInfoPanel(QWidget):
    """
    任务信息面板
    负责接收后端标准格式数据，转换为GUI组件需要的格式并显示
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._nav = NavigationPanel()
        layout = QVBoxLayout(self)
        layout.addWidget(self._nav)

        # 创建并注册任务专用视图
        self._table = GenericTableWidget(['序号', '任务类型', '区域', '子群', '状态'])
        self._gantt = GenericGanttChart()
        self._task_graph = GenericTaskGraphWidget()
        self._ltl = BodyLabel()

        self._nav.add_page(self._table, "tasks", "任务列表")
        self._nav.add_page(self._gantt, "gantt", "任务甘特图")
        self._nav.add_page(self._ltl, "ltl", "LTL公式")
        self._nav.add_page(self._task_graph, "graph", "任务关系图")

    def load_data(self, data: Dict[str, Any], graph_data: Dict[str, Any] = None):
        """
        从中介服务标准格式数据加载任务数据并显示
        
        参数：
            data: MediatorService.fetch_task_data()返回的标准格式数据
            {
                'tasks': [...],
                'ltl_formula': str,
                'current_time': float
            }
            graph_data: MediatorService.get_task_graph_data()返回的任务图数据（可选）
            {
                'nodes': [...],
                'edges': [...],
                'layout': {...},
                'style': {...}
            }
        """
        # 转换表格数据
        table_data = self._convert_to_table_data(data.get('tasks', []))
        
        # 转换甘特图数据
        gantt_data = self._convert_to_gantt_data(data)
        
        # 获取LTL公式
        ltl_text = data.get('ltl_formula', '暂无LTL公式')
        
        self._table.set_table_data(table_data)
        self._gantt.update_plot(gantt_data)
        self._ltl.setText(ltl_text)
        
        # 更新任务图（如果提供了图数据）
        if graph_data:
            self._task_graph.update_plot(graph_data)
    
    def _convert_to_table_data(self, tasks: List[Dict]) -> List[List[str]]:
        """将中介服务任务数据转换为表格数据"""
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
    
    def _convert_to_gantt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将中介服务任务数据转换为甘特图数据"""
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
            "current_time": data.get('current_time', 0),
            "y_label_fontsize": 10
        }
    
    def _format_task_status(self, status: str) -> str:
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

    # 保留向后兼容的接口（直接接收已转换的数据）
    def load_backend_data(self, backend_data: Dict[str, Any]):
        """向后兼容：使用旧方法名"""
        self.load_data(backend_data)
    
    def set_task_data_from_backend(self, backend_data: Dict[str, Any]):
        """向后兼容：使用旧方法名"""
        self.load_data(backend_data)
    
    def set_task_data(self, table_data, gantt_data, ltl_text):
        """向后兼容：直接设置已转换的任务数据"""
        self._table.set_table_data(table_data)
        self._gantt.update_plot(gantt_data)
        self._ltl.setText(ltl_text)
