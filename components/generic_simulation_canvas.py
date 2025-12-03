import pyqtgraph as pg


class GenericSimulationCanvas(pg.PlotWidget):
    """
    通用仿真画布（基于 pyqtgraph，极简版）

    职责：
    - 提供一个统一的 2D 画布容器（坐标轴 + 网格）
    - 配置基础外观（背景色、网格、等比例坐标）
    - 不参与任何业务绘制，不感知 scene_data 结构

    所有“画什么 / 怎么画”的逻辑应由后端或中介服务决定，
    通过 addItem/removeItem 等 pyqtgraph 接口直接操作本画布。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 统一外观配置
        self.setBackground("w")
        self.showGrid(x=True, y=True, alpha=0.3)
        # 锁定等比例坐标，避免图形被拉伸
        self.setAspectLocked(True)


