# 面板模块 (Panels)

面板模块负责UI业务逻辑，包括数据格式转换和用户交互处理。

## 模块概述

面板模块是UI层与中介服务层之间的桥梁，负责：
1. 接收标准格式的后端数据
2. 将数据转换为GUI特定的格式
3. 处理用户交互事件
4. 通过中介服务发送命令

## 核心面板

### 1. TaskInfoPanel（任务信息面板）

**文件：** `task_panel.py`

**功能：** 显示和管理任务信息

**主要功能：**
- 显示任务列表（表格形式）
- 显示任务甘特图（时间线）
- 显示LTL公式

**数据转换：**
- `load_data(data: Dict[str, Any])`：从中介服务加载标准格式数据
- `_convert_to_table_data(tasks: List[Dict])`：转换为表格数据
- `_convert_to_gantt_data(data: Dict[str, Any])`：转换为甘特图数据
- `_format_task_status(status: str)`：格式化任务状态（英文→中文）
- `_get_task_color(task_type: str)`：获取任务类型对应的颜色

**使用方法：**
```python
from panels import TaskInfoPanel

task_panel = TaskInfoPanel()

# 加载后端数据
task_data = mediator.fetch_task_data()
task_panel.load_data(task_data)
```

**向后兼容接口：**
- `load_backend_data()`：使用旧方法名
- `set_task_data_from_backend()`：使用旧方法名
- `set_task_data()`：直接设置已转换的数据

### 2. AgentInfoPanel（智能体信息面板）

**文件：** `agent_panel.py`

**功能：** 显示和管理智能体（无人机）信息

**主要功能：**
- 显示子群信息（表格）
- 显示己方智能体信息（表格）
- 显示敌方智能体信息（表格）
- 显示子群甘特图（时间线）
- 显示重规划甘特图（可选择不同子群）

**数据转换：**
- `load_data(data: Dict[str, Any])`：从中介服务加载标准格式数据
- `_convert_coalition_data(coalitions: List[Dict])`：转换子群数据
- `_convert_friendly_agent_data(agents: List[Dict])`：转换己方智能体数据
- `_convert_enemy_agent_data(agents: List[Dict])`：转换敌方智能体数据
- `_convert_unit_gantt_data(data: Dict[str, Any])`：转换子群甘特图数据
- `_convert_replan_gantt_data(data: Dict[str, Any])`：转换重规划甘特图数据
- `_format_status(status: str)`：格式化状态（英文→中文）
- `_format_members(members: List[int])`：格式化成员列表
- `_convert_schedule_to_bars(schedule: List[Dict])`：转换日程为甘特图条形数据

**使用方法：**
```python
from panels import AgentInfoPanel

agent_panel = AgentInfoPanel()

# 加载后端数据
agent_data = mediator.fetch_agent_data()
agent_panel.load_data(agent_data)
```

**向后兼容接口：**
- `load_backend_data()`：使用旧方法名
- `set_agent_data_from_backend()`：使用旧方法名
- `set_coalition_data()`：直接设置已转换的数据
- `set_friendly_agent_data()`：直接设置已转换的数据
- `set_enemy_agent_data()`：直接设置已转换的数据
- `set_unit_gantt_data()`：直接设置已转换的数据
- `set_replan_gantt_options()`：设置重规划选项
- `set_replan_gantt_data()`：设置重规划数据

### 3. CommandPanel（命令面板）

**文件：** `command_panel.py`

**功能：** 处理用户命令输入和发送

**主要功能：**
- 任务模板选择（自动填入instruction）
- 任务指令输入
- 任务创建
- 任务更新（选择任务ID和命令）
- 任务重规划
- 仿真控制

**数据获取：**
- `set_task_template_options(templates: List[str])`：设置任务模板选项
- `set_task_id_selection_options(task_ids: List[str])`：设置任务ID选项
- `set_command_selection_options(commands: List[str])`：设置命令选项

**用户输入：**
- `get_new_task_instruction() -> str`：获取新任务指令
- `get_task_template() -> str`：获取选中的任务模板
- `get_selected_task_update_info() -> tuple`：获取选中的任务更新信息

**命令发送：**
- `_on_create_task_clicked()`：处理"新增任务"按钮点击
- `_on_update_task_clicked()`：处理"修改任务"按钮点击
- `_on_replan_clicked()`：处理"任务重规划"按钮点击
- `_on_start_simulation_clicked()`：处理"开始仿真"按钮点击

**信号：**
- `command_executed`：命令执行成功时发出，用于触发数据刷新

**使用方法：**
```python
from panels import CommandPanel
from services import MediatorService

# 创建命令面板（需要传入MediatorService实例）
command_panel = CommandPanel(mediator)

# 设置选项（由主窗口自动调用）
command_panel.set_task_template_options(["模板1", "模板2"])
command_panel.set_task_id_selection_options(["1", "2", "3"])
command_panel.set_command_selection_options(["暂停", "恢复"])

# 连接信号（由主窗口自动连接）
command_panel.command_executed.connect(refresh_callback)
```

**特性：**
- 模板选择后自动填入instruction内容
- 刷新选项时保留当前选中值
- 防止刷新时覆盖用户输入

## 设计原则

### 1. 数据转换职责

面板负责将标准格式的后端数据转换为GUI特定的格式：
- 表格数据：二维列表格式
- 甘特图数据：包含tracks和bars的字典格式
- 状态文本：英文状态转换为中文显示

### 2. 用户交互处理

面板处理用户交互事件：
- 按钮点击
- 下拉框选择
- 文本输入

### 3. 命令构造

面板负责构造标准格式的命令数据：
- 创建任务命令
- 更新任务命令
- 重规划命令
- 仿真控制命令

### 4. 向后兼容

保留旧的方法名作为别名，确保向后兼容。

## 数据流

```
MediatorService.fetch_*_data() 
    → Panel.load_data() 
    → Panel._convert_*_data() 
    → Component.set_*_data()
```

```
User Interaction 
    → Panel._on_*_clicked() 
    → Panel构造command_data 
    → MediatorService.receive_command()
```

## 扩展指南

### 添加新的数据转换方法

1. 在面板类中添加新的转换方法（如`_convert_new_data()`）
2. 在`load_data()`中调用新方法
3. 确保转换后的数据格式符合组件要求

### 添加新的用户交互

1. 在UI文件中添加新的控件
2. 在`_connect_buttons()`中连接信号
3. 实现对应的处理方法（如`_on_new_button_clicked()`）
4. 构造命令数据并调用`mediator.receive_command()`

### 自定义显示格式

修改对应的格式化方法：
- `_format_task_status()`：自定义任务状态显示
- `_format_status()`：自定义智能体状态显示
- `_get_task_color()`：自定义任务类型颜色

## 注意事项

1. **数据格式一致性**：确保转换后的数据格式符合组件要求
2. **刷新时保留选择**：刷新选项时应该保留用户当前的选择
3. **防止覆盖用户输入**：避免在刷新时覆盖用户手动输入的内容
4. **错误处理**：处理无效数据或空数据的情况
5. **性能优化**：对于大量数据，考虑优化转换逻辑

## 与主窗口的集成

面板通过主窗口进行集成：

```python
# 主窗口创建面板
self.task_panel = TaskInfoPanel()
self.agent_panel = AgentInfoPanel()
self.command_panel = CommandPanel(self._mediator)

# 主窗口刷新数据
task_data = self._mediator.fetch_task_data()
self.task_panel.load_data(task_data)

# 主窗口连接信号
self.command_panel.command_executed.connect(self.refresh_all_panels)
```

## 参考实现

- `task_panel.py`：任务信息面板的完整实现
- `agent_panel.py`：智能体信息面板的完整实现
- `command_panel.py`：命令面板的完整实现

