# UI组件库说明

组件库（Components）提供了可复用的UI组件，用于构建各种数据可视化界面。

## 模块概述

组件库采用**通用化设计**，所有组件都接受标准化的数据格式，使得组件可以在不同场景下复用。组件基于PyQt5和第三方库（matplotlib、pyqtgraph、qfluentwidgets）构建。

## 核心组件

### 1. GenericTableWidget（通用表格组件）

**文件：** `generic_tablewidget.py`

**基类：** `qfluentwidgets.TableWidget`

**功能：** 显示结构化数据表格，支持自定义列标题。

**使用方法：**
```python
from components.generic_tablewidget import GenericTableWidget

# 创建表格，指定列标题
table = GenericTableWidget(['序号', '任务类型', '区域', '子群', '状态'])

# 设置数据（二维列表，每个内层列表是一行）
data = [
    ['1', 'patrol', 'A1', '0', '执行中'],
    ['2', 'surveillance', 'B2', '0', '待执行']
]
table.set_table_data(data)
```

**特性：**
- 自动居中对齐
- 支持最后一列自动拉伸
- 白色背景
- 圆角边框
- 粗体表头

### 2. GenericGanttChart（通用甘特图组件）

**文件：** `generic_ganntwidget.py`

**基类：** `matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg`

**功能：** 显示时间线甘特图，用于展示任务调度、资源分配等时间相关数据。

**使用方法：**
```python
from components.generic_ganntwidget import GenericGanttChart

gantt = GenericGanttChart()

# 设置甘特图数据
gantt_data = {
    "tracks": [
        {
            "label": "Unit-0",
            "bars": [
                {"start": 0, "duration": 5, "color": "silver", "text": "idle", "alpha": 0.8},
                {"start": 5, "duration": 5, "color": "lightblue", "text": "任务1", "alpha": 0.8}
            ]
        },
        {
            "label": "Unit-1",
            "bars": [
                {"start": 0, "duration": 3, "color": "lightgreen", "text": "任务2", "alpha": 0.8}
            ]
        }
    ],
    "current_time": 6.5,  # 可选，用于显示当前时间线
    "y_label_fontsize": 10
}
gantt.update_plot(gantt_data)
```

**数据格式：**
- `tracks`: 轨道列表，每个轨道代表一个实体（如子群、任务组）
- `bars`: 每个轨道上的条形数据，包含开始时间、持续时间、颜色、文本等
- `current_time`: 当前时间，用于绘制红色虚线时间线
- `y_label_fontsize`: Y轴标签字体大小

**特性：**
- 自动配置中文字体支持
- 支持多轨道显示
- 支持当前时间线标记
- 透明背景，适配主题

### 3. GenericSimulationCanvas（仿真画布组件）

**文件：** `generic_simul_canvas.py`

**基类：** `pyqtgraph.PlotWidget`

**功能：** 2D场景可视化，用于显示智能体、目标、区域和轨迹。

**使用方法：**
```python
from components.generic_simul_canvas import GenericSimulationCanvas

canvas = GenericSimulationCanvas()

# 更新场景数据
scene_data = {
    "agents": [
        {"id": 1, "x": 20, "y": 30, "color": "#FF5555", "symbol": "o"}
    ],
    "targets": [
        {"x": 30, "y": 40, "color": "#223399", "active": True}
    ],
    "regions": [
        {"type": "circle", "center": (35, 45), "radius": 8, "color": "#AAAAAA"}
    ],
    "trajectories": [
        {"points": [[10, 20], [15, 25], [20, 30]], "color": "#BB5555"}
    ],
    "time": 12.5,
    "limits": {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100}
}
canvas.update_scene(scene_data)
```

**支持的元素：**
- **智能体（Agents）**：散点图显示，支持不同颜色和符号
- **目标（Targets）**：散点图显示，支持激活/非激活状态
- **区域（Regions）**：支持圆形和多边形
- **轨迹（Trajectories）**：折线显示

**特性：**
- 实时更新场景
- 支持网格显示
- 锁定纵横比
- 自动设置坐标轴范围

**支持的符号：**
pyqtgraph支持的符号：`'o'`（圆形）、`'s'`（方形）、`'t'`（三角形）、`'d'`（菱形）、`'+'`（加号）

### 4. SelectorChartWidget（选择器图表组件）

**文件：** `selectorchartwidget.py`

**基类：** `PyQt5.QtWidgets.QWidget`

**功能：** 组合下拉选择器和图表，用于切换显示不同实体的图表数据。

**使用方法：**
```python
from components.selectorchartwidget import SelectorChartWidget

widget = SelectorChartWidget()

# 设置选项列表
widget.set_options(['Unit-0', 'Unit-1', 'Unit-2'])

# 为每个选项设置图表数据
widget.set_chart_data_for_option('Unit-0', gantt_data_0)
widget.set_chart_data_for_option('Unit-1', gantt_data_1)
widget.set_chart_data_for_option('Unit-2', gantt_data_2)
```

**应用场景：**
- 重规划甘特图：选择不同子群查看其重规划方案
- 多实体对比：切换查看不同实体的数据

**特性：**
- 自动响应选择变化
- 内部使用`GenericGanttChart`显示图表
- 使用`qfluentwidgets.EditableComboBox`作为选择器

### 5. NavigationPanel（导航面板组件）

**文件：** `navi_panel.py`

**基类：** `PyQt5.QtWidgets.QWidget`

**功能：** 提供分段导航界面，用于在多个页面之间切换。

**使用方法：**
```python
from components.navi_panel import NavigationPanel

nav = NavigationPanel()

# 添加页面
table_widget = GenericTableWidget(['列1', '列2'])
gantt_widget = GenericGanttChart()

nav.add_page(table_widget, "table", "表格视图")
nav.add_page(gantt_widget, "gantt", "甘特图视图")

# 切换到指定页面
nav.set_current_page("gantt")
```

**应用场景：**
- 任务面板：在任务列表、甘特图、LTL公式之间切换
- 智能体面板：在子群信息、无人机信息、甘特图之间切换

**特性：**
- 使用`qfluentwidgets.SegmentedWidget`作为导航栏
- 使用`QStackedWidget`管理页面
- 支持动态添加页面

### 6. GenericPlotCanvas（通用绘图画布）

**文件：** `generic_plotcanvas.py`

**基类：** `matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg`

**功能：** 基础绘图画布，提供matplotlib集成，可被子类继承扩展。

**使用方法：**
```python
from components.generic_plotcanvas import GenericPlotCanvas

canvas = GenericPlotCanvas()

# 更新绘图数据
plot_data = {
    "x": [1, 2, 3, 4, 5],
    "y": [0.1, 0.5, 0.9, 0.7, 0.3],
    "title": "性能指标"
}
canvas.update_plot(plot_data)
```

**特性：**
- 自动配置中文字体支持
- 提供基础绘图功能
- 可被子类继承扩展

### 7. MatplotlibFontConfig（matplotlib字体配置）

**文件：** `matplotlib_font_config.py`

**功能：** 统一配置matplotlib使用中文字体，解决中文显示问题。

**使用方法：**
```python
from components.matplotlib_font_config import setup_chinese_font

# 在创建matplotlib组件前调用
setup_chinese_font()
```

**字体优先级：**
1. SimHei（黑体）
2. Microsoft YaHei（微软雅黑）
3. WenQuanYi Micro Hei（文泉驿微米黑）
4. STHeiti（华文黑体）
5. SimSun（宋体）
6. DejaVu Sans（备用）

**特性：**
- 自动检测系统可用字体
- 按优先级选择最佳字体
- 解决负号显示问题
- 所有matplotlib组件自动使用此配置

## 设计原则

### 1. 标准化数据格式

所有组件都接受标准化的数据格式，使得数据在不同组件间可以轻松传递。

### 2. 可复用性

组件设计为通用组件，不绑定特定业务逻辑，可以在不同场景下复用。

### 3. 组合优于继承

通过组合小组件构建复杂界面，而不是创建庞大的单一组件。

### 4. 中文支持

所有组件都考虑了中文显示需求，特别是matplotlib相关组件。

## 使用示例

### 创建任务面板

```python
from components.navi_panel import NavigationPanel
from components.generic_tablewidget import GenericTableWidget
from components.generic_ganntwidget import GenericGanttChart

# 创建导航面板
nav = NavigationPanel()

# 创建子组件
table = GenericTableWidget(['序号', '任务类型', '区域', '子群', '状态'])
gantt = GenericGanttChart()

# 添加到导航面板
nav.add_page(table, "table", "任务列表")
nav.add_page(gantt, "gantt", "任务甘特图")
```

### 创建智能体面板

```python
from components.navi_panel import NavigationPanel
from components.generic_tablewidget import GenericTableWidget
from components.generic_ganntwidget import GenericGanttChart
from components.selectorchartwidget import SelectorChartWidget

nav = NavigationPanel()

coalition_table = GenericTableWidget(['子群序号', '当前任务', '成员结构'])
agent_table = GenericTableWidget(['无人机序号', '类型', '子群序号', '当前状态'])
unit_gantt = GenericGanttChart()
replan_gantt = SelectorChartWidget()

nav.add_page(coalition_table, "coalitions", "子群信息")
nav.add_page(agent_table, "agents", "无人机信息")
nav.add_page(unit_gantt, "unit_gantt", "子群甘特图")
nav.add_page(replan_gantt, "replan_gantt", "无人机重规划甘特图")
```

## 扩展指南

### 创建新组件

1. 确定组件基类（QWidget、FigureCanvas等）
2. 设计标准化数据格式
3. 实现数据更新方法（如`update_plot`、`set_data`等）
4. 考虑中文显示支持
5. 添加必要的样式和配置

### 修改现有组件

1. 保持向后兼容的数据格式
2. 如需修改数据格式，更新所有使用该组件的地方
3. 更新相关文档

## 注意事项

1. **数据格式一致性**：确保传入的数据格式符合组件期望
2. **线程安全**：所有UI更新应在主线程进行
3. **性能优化**：对于频繁更新的组件（如仿真画布），考虑优化更新逻辑
4. **字体配置**：matplotlib组件会自动调用字体配置，无需手动配置

