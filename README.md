# 机器人GUI系统

一个基于PyQt5的机器人任务管理和仿真可视化系统，采用分层架构设计，支持灵活的后端适配。

![示例界面](example.png)

## 项目概述

本项目提供了一个完整的GUI界面，用于：
- 管理和监控机器人任务
- 可视化智能体（无人机）状态和子群信息
- 实时显示仿真场景
- 发送控制命令到后端系统

## 项目结构

```
GUI/
├── main_window.py                 # 主窗口入口，整合所有面板
├── example_mediator_service.py   # 示例中介服务（用于测试）
├── panels/                       # 面板模块（UI业务逻辑层）
│   ├── task_panel.py            # 任务信息面板
│   ├── agent_panel.py           # 智能体信息面板
│   └── command_panel.py         # 命令输入面板
├── services/                     # 服务层（中介服务接口）
│   ├── mediator_service.py     # 中介服务抽象基类
│   └── __init__.py             # 服务模块导出
├── components/                   # 可复用UI组件
│   ├── generic_simul_canvas.py    # 仿真画布组件
│   ├── generic_tablewidget.py     # 通用表格组件
│   ├── generic_ganntwidget.py     # 通用甘特图组件
│   ├── generic_plotcanvas.py     # 通用绘图画布
│   ├── selectorchartwidget.py     # 选择器图表组件
│   ├── navi_panel.py              # 导航面板组件
│   └── matplotlib_font_config.py  # matplotlib中文字体配置
└── ui/                           # UI设计文件（Qt Designer生成）
    ├── UI_HomeInterface.py
    └── UI_CommandInterface.py
```

## 快速开始

### 环境要求

- Python 3.7+
- PyQt5
- qfluentwidgets
- pyqtgraph
- matplotlib

### 安装依赖

```bash
pip install PyQt5 qfluentwidgets pyqtgraph matplotlib
```

### 运行程序

```bash
python main_window.py
```

## 架构设计

### 分层架构

系统采用清晰的三层架构：

1. **UI层（Panels）**：负责界面展示和用户交互
   - `TaskInfoPanel`：任务信息展示
   - `AgentInfoPanel`：智能体信息展示
   - `CommandPanel`：命令输入和发送

2. **中介服务层（MediatorService）**：负责数据转换和命令处理
   - `DataProvider`：从后端获取数据（后端→UI）
   - `CommandHandler`：处理UI命令（UI→后端）
   - `MediatorService`：统一的中介服务接口

3. **组件层（Components）**：提供可复用的UI组件
   - 表格、甘特图、仿真画布等通用组件

### 数据流

```
后端系统 → MediatorService (DataProvider) → Panels → UI组件
UI组件 → Panels → MediatorService (CommandHandler) → 后端系统
```

### 依赖注入

系统采用依赖注入模式，通过构造函数注入中介服务，使得系统可以灵活切换不同的后端实现。

**示例：**
```python
from main_window import MainWindow
from example_mediator_service import ExampleMediatorService

# 创建中介服务
mediator = ExampleMediatorService()

# 创建主窗口（依赖注入）
main_window = MainWindow(mediator=mediator)
main_window.show()
```

## 主要功能模块

### 1. 主窗口 (`main_window.py`)

主窗口整合了所有功能面板，包括：
- **任务信息面板**：显示任务列表、甘特图和LTL公式
- **智能体信息面板**：显示子群信息、无人机信息和甘特图
- **仿真画布**：实时显示仿真场景中的智能体、目标和区域
- **命令面板**：输入和发送控制命令

**特性：**
- 自动数据刷新（每1秒）
- 仿真时间步进（每100ms，当仿真运行时）
- 命令执行后自动刷新数据

### 2. 面板模块 (`panels/`)

面板模块负责UI业务逻辑，包括数据格式转换和用户交互处理。

**核心面板：**
- `TaskInfoPanel`：任务信息展示和格式化
- `AgentInfoPanel`：智能体信息展示和格式化
- `CommandPanel`：命令输入、模板选择和命令发送

**设计特点：**
- 面板接收标准格式的后端数据
- 面板内部负责GUI特定的数据转换
- 面板通过`MediatorService`与后端交互

详细说明请参考 [panels/README.md](panels/README.md)

### 3. 中介服务层 (`services/`)

中介服务层定义了统一的后端接口，实现数据隔离和职责分离。

**核心接口：**
- `DataProvider`：数据提供者接口（后端→UI）
- `CommandHandler`：命令处理器接口（UI→后端）
- `MediatorService`：统一的中介服务接口

**扩展后端：**
要实现自定义后端，只需继承`MediatorService`并实现所有抽象方法。参考`example_mediator_service.py`。

详细说明请参考 [services/README.md](services/README.md)

### 4. UI组件 (`components/`)

提供可复用的UI组件，包括：
- **表格组件**：用于显示结构化数据
- **甘特图组件**：用于显示时间线任务
- **仿真画布**：用于2D场景可视化
- **导航面板**：用于多页面切换

详细说明请参考 [components/README.md](components/README.md)

### 5. 示例中介服务 (`example_mediator_service.py`)

提供模拟数据用于开发和测试，展示了如何实现`MediatorService`接口。

**功能：**
- 模拟智能体数据（子群、无人机）
- 模拟任务数据
- 模拟仿真场景数据
- 模拟命令处理

## 使用指南

### 1. 使用示例中介服务

直接运行`main_window.py`即可使用示例中介服务，查看模拟数据。

### 2. 连接真实后端

1. 创建自定义中介服务类，继承`MediatorService`
2. 实现所有抽象方法：
   - `fetch_agent_data()`：获取智能体数据
   - `fetch_task_data()`：获取任务数据
   - `fetch_simulation_scene()`：获取仿真场景数据
   - `receive_command()`：接收UI命令
   - `get_task_templates()`：获取任务模板列表
   - `get_task_ids()`：获取任务ID列表
   - `get_command_options()`：获取命令选项列表
3. 可选实现：
   - `get_task_template_content()`：获取模板详细内容
   - `is_simulation_running()`：检查仿真状态
   - `step_simulation()`：推进仿真时间步
4. 在创建`MainWindow`时传入自定义中介服务实例

```python
from main_window import MainWindow
from your_mediator import YourMediatorService

mediator = YourMediatorService()
main_window = MainWindow(mediator=mediator)
main_window.show()
```

### 3. 数据刷新机制

- **自动刷新**：系统每1秒自动刷新一次数据
- **仿真更新**：仿真时间每100ms更新一次（当仿真运行时）
- **命令触发**：命令执行成功后自动刷新数据
- **手动刷新**：可通过`refresh_all_panels()`方法手动刷新

### 4. 发送命令

通过命令面板可以发送以下类型的命令：

1. **创建任务** (`create_task`)：
   - 输入任务指令
   - 选择任务模板（可选）
   - 点击"新增任务"按钮

2. **更新任务** (`update_task`)：
   - 选择任务ID
   - 选择命令选项（暂停、恢复等）
   - 点击"修改任务"按钮

3. **任务重规划** (`replan`)：
   - 点击"任务重规划"按钮

4. **开始仿真** (`start_simulation`)：
   - 点击"开始仿真"按钮

### 5. 模板功能

- 选择任务模板后，会自动将模板内容填入instruction输入框
- 模板内容由中介服务提供，可通过`get_task_template_content()`方法获取

## 详细文档

- [面板模块说明](panels/README.md)
- [中介服务说明](services/README.md)
- [组件库说明](components/README.md)
- [UI设计文件说明](ui/README.md)

## 开发说明

### 代码规范

- 使用类型提示（typing）
- 遵循PEP 8代码风格
- 使用中文注释和文档字符串

### 扩展指南

1. **添加新的面板**：在`panels/`目录下创建新面板类
2. **添加新的组件**：在`components/`目录下创建新组件
3. **实现新的中介服务**：继承`MediatorService`并实现所有抽象方法
4. **修改UI布局**：使用Qt Designer编辑`.ui`文件，然后重新生成Python代码

### 命名约定

- **类名**：使用PascalCase（如`MainWindow`、`TaskInfoPanel`）
- **方法名**：使用snake_case（如`refresh_all_panels`、`load_data`）
- **私有成员**：使用下划线前缀（如`_mediator`、`_is_refreshing_options`）
- **常量**：使用全大写（如`MAX_RETRY_COUNT`）

## 常见问题

### Q: 如何添加新的数据源？

A: 创建新的`MediatorService`子类，实现所有抽象方法，然后在创建`MainWindow`时传入该实例。

### Q: 如何自定义面板的显示格式？

A: 修改对应面板类中的数据转换方法（如`_convert_to_table_data`、`_format_task_status`等）。

### Q: 如何添加新的命令类型？

A: 在`CommandPanel`中添加新的按钮和处理方法，调用`mediator.receive_command()`发送命令。

### Q: 下拉框选择后自动跳回第一项？

A: 已修复。刷新选项时会保留当前选中值，不会重置。

## 许可证

MIT License

Copyright (c) 2025 Luo Yinhang

## 联系方式

yinhang.luo@pku.edu.cn
