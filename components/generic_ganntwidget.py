# ui/widgets/gantt_chart.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from MultiAgentGUI.themes.matplotlib_font_config import setup_chinese_font


class GenericGanttChart(FigureCanvas):
    """通用甘特图组件，接受标准化绘图指令"""
    def __init__(self):
        # 配置matplotlib使用中文字体（SimHei黑体）
        setup_chinese_font()
        
        self.fig = Figure(facecolor="none")
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("none")

    def update_plot(self, gantt_data: dict):
        """
        接受标准化甘特图数据，格式如下：
        {
            "tracks": [
                {
                    "label": "Unit 0",
                    "bars": [
                        {"start": 0, "duration": 5, "color": "silver", "text": "idle"},
                        {"start": 5, "duration": 3, "color": "lightblue", "text": "task1"}
                    ]
                },
                ...
            ],
            "current_time": 10,  # 可选，用于画时间线
            "y_label_fontsize": 10
        }
        """
        self.ax.clear()
        tracks = gantt_data.get("tracks", [])
        if not tracks:
            self.ax.axis('off')
            self.draw()
            return

        interval = 5
        height = 2
        y_margin = 1

        for idx, track in enumerate(tracks):
            y_base = interval * idx + y_margin
            for bar in track.get("bars", []):
                self.ax.broken_barh(
                    [(bar["start"], bar["duration"])],
                    [y_base, height],
                    facecolors=bar.get("color", "gray"),
                    edgecolor="k",
                    alpha=bar.get("alpha", 1.0)
                )
                if bar.get("text"):
                    self.ax.text(
                        x=bar["start"] + 0.5,
                        y=y_base + height + 0.2,
                        s=bar["text"],
                        fontsize=bar.get("fontsize", 8)
                    )

        # 设置 Y 轴
        y_ticks = [y_margin + height / 2 + interval * i for i in range(len(tracks))]
        y_labels = [track.get("label", f"Track {i}") for i, track in enumerate(tracks)]
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels(y_labels, fontsize=gantt_data.get("y_label_fontsize", 10))
        self.ax.tick_params(axis='y', length=0)
        self.ax.tick_params(axis='x', length=0)

        # 当前时间线
        if "current_time" in gantt_data:
            self.ax.axvline(
                x=gantt_data["current_time"],
                color='red',
                linestyle='--',
                linewidth=1
            )

        self.draw()