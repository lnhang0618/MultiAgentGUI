# ui/widgets/simulation_canvas.py
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from typing import List, Tuple, Optional


class GenericSimulationCanvas(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackground("w")
        self.showGrid(x=True, y=True)
        self.setAspectLocked(True)

        self._agents_layer = pg.ScatterPlotItem(size=15)
        self._targets_layer = pg.ScatterPlotItem(size=10)
        self._regions_layer = []
        self._trajectories_layer = []

        self.addItem(self._agents_layer)
        self.addItem(self._targets_layer)

    def update_scene(self, scene_data: dict):
        """
        接受标准化场景数据：
        {
            "agents": [
                {"x": 10, "y": 20, "color": "#BB5555", "symbol": "p", "id": 1}
            ],
            "targets": [
                {"x": 30, "y": 40, "color": "#223399", "active": True}
            ],
            "regions": [
                {"type": "circle", "center": (50,60), "radius": 10, "color": "#AAAAAA"},
                {"type": "polygon", "points": [[70,80], [90,80], [80,100]], "color": "#DDD700"}
            ],
            "trajectories": [
                {"points": [[10,20], [15,25], [20,30]], "color": "#BB5555"}
            ],
            "time": 12.5,
            "limits": {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100}
        }
        """
        # Update agents
        if "agents" in scene_data:
            agents = scene_data["agents"]
            self._agents_layer.setData(
                x=[a["x"] for a in agents],
                y=[a["y"] for a in agents],
                brush=[pg.mkBrush(a["color"]) for a in agents],
                symbol=[a.get("symbol", "o") for a in agents]
            )

        # Update targets
        if "targets" in scene_data:
            targets = [t for t in scene_data["targets"] if t.get("active", True)]
            self._targets_layer.setData(
                x=[t["x"] for t in targets],
                y=[t["y"] for t in targets],
                brush=[pg.mkBrush(t["color"]) for t in targets]
            )

        # Update regions (simplified: clear and redraw)
        for item in self._regions_layer:
            self.removeItem(item)
        self._regions_layer.clear()

        for region in scene_data.get("regions", []):
            if region["type"] == "circle":
                item = self._draw_circle(region["center"], region["radius"], region["color"])
            elif region["type"] == "polygon":
                item = self._draw_polygon(region["points"], region["color"])
            self._regions_layer.append(item)

        # Update trajectories
        for item in self._trajectories_layer:
            self.removeItem(item)
        self._trajectories_layer.clear()

        for traj in scene_data.get("trajectories", []):
            item = pg.PlotDataItem(
                x=[p[0] for p in traj["points"]],
                y=[p[1] for p in traj["points"]],
                pen=pg.mkPen(traj["color"], width=2)
            )
            self.addItem(item)
            self._trajectories_layer.append(item)

        # Update limits
        # pyqtgraph的setLimits使用驼峰命名：xMin, xMax, yMin, yMax
        if "limits" in scene_data:
            lim = scene_data["limits"]
            # 转换下划线命名为驼峰命名
            limits_kwargs = {}
            if "x_min" in lim:
                limits_kwargs["xMin"] = lim["x_min"]
            if "x_max" in lim:
                limits_kwargs["xMax"] = lim["x_max"]
            if "y_min" in lim:
                limits_kwargs["yMin"] = lim["y_min"]
            if "y_max" in lim:
                limits_kwargs["yMax"] = lim["y_max"]
            # 也支持直接传入驼峰命名（向后兼容）
            for key in ["xMin", "xMax", "yMin", "yMax"]:
                if key in lim:
                    limits_kwargs[key] = lim[key]
            if limits_kwargs:
                self.setLimits(**limits_kwargs)

    def _draw_circle(self, center, radius, color):
        # QGraphicsEllipseItem 在 QtWidgets 模块中
        item = QtWidgets.QGraphicsEllipseItem(center[0]-radius, center[1]-radius, 2*radius, 2*radius)
        item.setPen(pg.mkPen("w"))
        item.setBrush(pg.mkBrush(color))
        self.addItem(item)
        return item

    def _draw_polygon(self, points, color):
        # QGraphicsPolygonItem 在 QtWidgets 模块中，QPolygonF 在 QtGui 模块中
        poly = QtWidgets.QGraphicsPolygonItem(QtGui.QPolygonF([QtCore.QPointF(x, y) for x, y in points]))
        poly.setPen(pg.mkPen("w"))
        poly.setBrush(pg.mkBrush(color))
        self.addItem(poly)
        return poly