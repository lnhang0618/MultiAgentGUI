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
        self.agent_table = GenericTableWidget(['智能体编号', '类型', '子群序号', '当前状态'])
        self.unit_gantt = GenericGanttChart()
        self.replan_gantt = SelectorChartWidget()  # 用于重规划甘特图

        # 注册页面
        self.nav.add_page(self.coalition_table, "coalitions", "子群信息")
        self.nav.add_page(self.agent_table, "agents", "智能体信息")
        self.nav.add_page(self.unit_gantt, "unit_gantt", "子群甘特图")
        self.nav.add_page(self.replan_gantt, "replan_gantt", "智能体重规划甘特图")

    # 提供数据注入接口
    def set_coalition_data(self, data): 
        self.coalition_table.set_table_data(data)

    def set_agent_data(self, data): 
        self.agent_table.set_table_data(data)

    def set_unit_gantt_data(self, data): 
        self.unit_gantt.update_plot(data)

    def set_replan_gantt_options(self, options): 
        self.replan_gantt.set_options(options)

    def set_replan_gantt_data(self, option_key, data): 
        self.replan_gantt.set_chart_data_for_option(option_key, data)