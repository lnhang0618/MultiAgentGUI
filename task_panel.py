# task_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from components.navi_panel import NavigationPanel
from components.generic_tablewidget import GenericTableWidget
from components.generic_ganntwidget import GenericGanttChart
from qfluentwidgets import BodyLabel


class TaskInfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._nav = NavigationPanel()
        layout = QVBoxLayout(self)
        layout.addWidget(self._nav)

        # 创建并注册任务专用视图
        self._table = GenericTableWidget(['序号', '任务类型', '区域', '子群', '状态'])
        self._gantt = GenericGanttChart()
        self._ltl = BodyLabel()

        self._nav.add_page(self._table, "tasks", "任务列表")
        self._nav.add_page(self._gantt, "gantt", "任务甘特图")
        self._nav.add_page(self._ltl, "ltl", "LTL公式")

    def set_task_data(self, table_data, gantt_data, ltl_text):
        self._table.set_table_data(table_data)
        self._gantt.update_plot(gantt_data)
        self._ltl.setText(ltl_text)