from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .matplotlib_font_config import setup_chinese_font


class GenericPlotCanvas(FigureCanvas):
    def __init__(self):
        # 配置matplotlib使用中文字体（SimHei黑体）
        setup_chinese_font()
        
        self.fig = Figure()
        super().__init__(self.fig)

    def update_plot(self, plot_data: dict):
        """
        Override in subclass.
        plot_data should be flat, e.g.:
        {"x": [1,2,3], "y": [0.1,0.5,0.9], "title": "Performance"}
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(plot_data.get("x", []), plot_data.get("y", []))
        ax.set_title(plot_data.get("title", ""))
        self.draw()