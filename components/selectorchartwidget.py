# ui/widgets/selector_chart.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import EditableComboBox
from .generic_ganntwidget import GenericGanttChart


class SelectorChartWidget(QWidget):
    """通用选择器+图表容器，用于切换不同实体的图表"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        
        self.combobox = EditableComboBox()
        self.chart = GenericGanttChart()
        
        self.layout().addWidget(self.combobox)
        self.layout().addWidget(self.chart)
        
        self._chart_data_map = {}  # {option_key: chart_data}
        self.combobox.currentTextChanged.connect(self._on_selection_changed)

    def set_options(self, options: list):
        """设置选择项，如 ['Unit-0', 'Unit-1']"""
        self.combobox.clear()
        self.combobox.addItems(options)

    def set_chart_data_for_option(self, option_key: str, chart_data: dict):
        """为某个选项预设图表数据"""
        self._chart_data_map[option_key] = chart_data

    def _on_selection_changed(self, selected_key: str):
        data = self._chart_data_map.get(selected_key)
        if data is not None:
            self.chart.update_plot(data)