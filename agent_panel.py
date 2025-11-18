# agent_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from components.navi_panel import NavigationPanel
from components.generic_tablewidget import GenericTableWidget
from components.generic_ganntwidget import GenericGanttChart
from components.selectorchartwidget import SelectorChartWidget


class AgentInfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.nav = NavigationPanel()
        layout.addWidget(self.nav)

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

    # 提供数据注入接口
    def set_coalition_data(self, data): 
        self.coalition_table.set_table_data(data)

    def set_friendly_agent_data(self, data): 
        """设置己方智能体数据"""
        self.friendly_agent_table.set_table_data(data)
    
    def set_enemy_agent_data(self, data): 
        """设置敌方智能体数据"""
        self.enemy_agent_table.set_table_data(data)

    def set_unit_gantt_data(self, data): 
        self.unit_gantt.update_plot(data)

    def set_replan_gantt_options(self, options): 
        self.replan_gantt.set_options(options)

    def set_replan_gantt_data(self, option_key, data): 
        self.replan_gantt.set_chart_data_for_option(option_key, data)