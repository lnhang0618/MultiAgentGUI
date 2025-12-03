# panels/agent_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from typing import List, Dict, Any
from MultiAgentGUI.components.navi_panel import NavigationPanel
from MultiAgentGUI.components.generic_tablewidget import GenericTableWidget
from MultiAgentGUI.components.generic_ganntwidget import GenericGanttChart
from MultiAgentGUI.components.selectorchartwidget import SelectorChartWidget
from MultiAgentGUI.components.panel_header import PanelHeader
from MultiAgentGUI.themes import Theme
from MultiAgentGUI.adapters.agent_data_adapter import AgentDataAdapter


class AgentInfoPanel(QWidget):
    """
    Agent信息面板
    负责接收后端标准格式数据，转换为GUI组件需要的格式并显示
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏：颜色使用 Theme 中为智能体面板配置的 header 颜色
        self.header = PanelHeader(
            "智能体信息",
            bg_color=Theme.PANEL_AGENT_HEADER_BG,
            border_color=Theme.PANEL_AGENT_HEADER_BORDER,
            left_bar_color=Theme.PANEL_AGENT_HEADER_BORDER,
            # 标题文字使用智能体面板的主题深色，而不是全局主文字色
            text_color=Theme.PANEL_AGENT_HEADER_BORDER,
        )
        layout.addWidget(self.header)
        
        # 创建内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {Theme.PANEL_AGENT_BG};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.nav = NavigationPanel()
        content_layout.addWidget(self.nav)
        
        layout.addWidget(content_widget)

        # 创建通用组件
        self.coalition_table = GenericTableWidget(['子群序号', '当前任务', '成员结构'])
        # 己方智能体表：包含完整信息（编号、类型、子群序号、当前状态）
        self.friendly_agent_table = GenericTableWidget(['智能体编号', '类型', '子群序号', '当前状态'])
        # 敌方智能体表：只包含可获取的信息（编号、类型、当前状态），不包含子群序号
        self.enemy_agent_table = GenericTableWidget(['智能体编号', '类型', '当前状态'])
        self.unit_gantt = GenericGanttChart()
        self.replan_gantt = SelectorChartWidget()  # 用于重规划甘特图

        # 注册页面
        self.nav.add_page(self.coalition_table, "coalitions", "子群信息")
        self.nav.add_page(self.friendly_agent_table, "friendly_agents", "己方智能体")
        self.nav.add_page(self.enemy_agent_table, "enemy_agents", "敌方智能体")
        self.nav.add_page(self.unit_gantt, "unit_gantt", "子群甘特图")
        self.nav.add_page(self.replan_gantt, "replan_gantt", "子群重规划甘特图")

    def load_data(self, data: Dict[str, Any]):
        """
        从中介服务标准格式数据加载Agent数据并显示
        
        参数：
            data: MediatorService.fetch_agent_data()返回的标准格式数据
            {
                'coalitions': [...],
                'agents': [...],
                'current_time': float
            }
        """
        # 使用适配器转换数据
        coalition_data = AgentDataAdapter.convert_coalition_table_data(data.get('coalitions', []))
        self.coalition_table.set_table_data(coalition_data)
        
        friendly_data = AgentDataAdapter.convert_friendly_agent_table_data(data.get('agents', []))
        self.friendly_agent_table.set_table_data(friendly_data)
        
        enemy_data = AgentDataAdapter.convert_enemy_agent_table_data(data.get('agents', []))
        self.enemy_agent_table.set_table_data(enemy_data)
        
        unit_gantt_data = AgentDataAdapter.convert_unit_gantt_data(data)
        self.unit_gantt.update_plot(unit_gantt_data)
        
        replan_options = AgentDataAdapter.get_replan_options(data.get('coalitions', []))
        self.replan_gantt.set_options(replan_options)
        
        replan_data_map = AgentDataAdapter.convert_replan_gantt_data(data)
        for option_key, gantt_data in replan_data_map.items():
            self.replan_gantt.set_chart_data_for_option(option_key, gantt_data)
