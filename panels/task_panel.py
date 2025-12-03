# panels/task_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from typing import List, Tuple, Dict, Any
from MultiAgentGUI.components.navi_panel import NavigationPanel
from MultiAgentGUI.components.generic_tablewidget import GenericTableWidget
from MultiAgentGUI.components.generic_ganntwidget import GenericGanttChart
from MultiAgentGUI.components.generic_taskgraphwidget import GenericTaskGraphWidget
from MultiAgentGUI.components.panel_header import PanelHeader
from MultiAgentGUI.themes import Theme
from MultiAgentGUI.adapters.task_data_adapter import TaskDataAdapter
from qfluentwidgets import BodyLabel


class TaskInfoPanel(QWidget):
    """
    任务信息面板
    负责接收后端标准格式数据，转换为GUI组件需要的格式并显示
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏：颜色使用 Theme 中为任务面板配置的 header 颜色
        self.header = PanelHeader(
            "任务信息",
            bg_color=Theme.PANEL_TASK_HEADER_BG,
            border_color=Theme.PANEL_TASK_HEADER_BORDER,
            left_bar_color=Theme.PANEL_TASK_HEADER_BORDER,
            # 标题文字使用任务面板的主题深色，而不是全局主文字色
            text_color=Theme.PANEL_TASK_HEADER_BORDER,
        )
        layout.addWidget(self.header)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {Theme.PANEL_TASK_BG};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self._nav = NavigationPanel()
        content_layout.addWidget(self._nav)
        
        layout.addWidget(content_widget)

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
        # 使用适配器转换数据
        table_data = TaskDataAdapter.convert_table_data(data.get('tasks', []))
        gantt_data = TaskDataAdapter.convert_gantt_data(data)
        
        # 获取LTL公式
        ltl_text = data.get('ltl_formula', '暂无LTL公式')
        
        self._table.set_table_data(table_data)
        self._gantt.update_plot(gantt_data)
        self._ltl.setText(ltl_text)
        
        # 更新任务图（如果提供了图数据）
        if graph_data:
            self._task_graph.update_plot(graph_data)
