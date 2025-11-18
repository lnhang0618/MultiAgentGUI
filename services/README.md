# 服务层模块说明

服务层（Services Layer）是系统的核心业务逻辑层，负责数据格式转换和与后端系统的交互。

## 模块概述

服务层采用**适配器模式**和**依赖注入**设计，将后端数据格式转换为GUI需要的统一格式。这种设计使得系统可以灵活切换不同的后端实现，而无需修改UI层代码。

## 核心组件

### 1. BackendAdapter（后端适配器抽象基类）

**文件：** `backend_adapter.py`

**作用：** 定义所有后端必须实现的统一接口，是系统与后端通信的抽象层。

**关键方法：**
- `fetch_agent_data()` - 获取智能体相关数据（子群、无人机等）
- `fetch_task_data()` - 获取任务相关数据
- `fetch_simulation_scene(timestamp)` - 获取仿真场景数据
- `send_command(command_data)` - 向后端发送命令
- `get_task_templates()` - 获取任务模板列表
- `get_task_ids()` - 获取当前任务ID列表
- `get_command_options()` - 获取可用命令选项

**使用方式：**
```python
from services.backend_adapter import BackendAdapter

class YourBackendAdapter(BackendAdapter):
    def fetch_agent_data(self):
        # 实现从真实后端获取数据
        pass
    
    # 实现其他抽象方法...
```

### 2. AgentService（智能体服务）

**文件：** `agent_service.py`

**作用：** 处理智能体（Agent）相关的数据转换，将后端原始数据转换为GUI需要的格式。

**主要功能：**
- 子群数据转换：将后端子群数据转换为表格格式
- 无人机数据转换：将后端无人机数据转换为表格格式
- 甘特图数据转换：将后端日程数据转换为甘特图格式
- 重规划甘特图数据转换：处理重规划相关的甘特图数据

**关键方法：**
- `get_coalition_data_for_gui()` - 获取子群表格数据
- `get_agent_data_for_gui()` - 获取无人机表格数据
- `get_unit_gantt_data_for_gui()` - 获取子群甘特图数据
- `get_replan_gantt_options()` - 获取重规划选项列表
- `get_replan_gantt_data_for_gui()` - 获取重规划甘特图数据

**数据格式示例：**
```python
# 子群表格数据格式
[
    ['0', '任务1-巡逻', '3个成员 [1, 2, 3]'],
    ['1', '任务3-搜索', '2个成员 [4, 5]']
]

# 甘特图数据格式
{
    "tracks": [
        {
            "label": "Unit-0",
            "bars": [
                {"start": 0, "duration": 5, "color": "silver", "text": "idle", "alpha": 0.8},
                {"start": 5, "duration": 5, "color": "lightblue", "text": "任务1-巡逻", "alpha": 0.8}
            ]
        }
    ],
    "current_time": 10,
    "y_label_fontsize": 10
}
```

### 3. TaskService（任务服务）

**文件：** `task_service.py`

**作用：** 处理任务（Task）相关的数据转换。

**主要功能：**
- 任务表格数据转换
- 任务甘特图数据转换
- LTL公式提取

**关键方法：**
- `get_task_data_for_gui()` - 获取任务数据（表格、甘特图、LTL公式）

**返回格式：**
```python
(
    table_data,    # List[List[str]] - 表格数据
    gantt_data,    # Dict - 甘特图数据
    ltl_text       # str - LTL公式文本
)
```

**任务状态映射：**
- `pending` → `待执行`
- `executing` → `执行中`
- `completed` → `已完成`
- `failed` → `失败`
- `cancelled` → `已取消`

**任务类型颜色映射：**
- `patrol` → `lightblue`
- `surveillance` → `lightgreen`
- `search` → `lightyellow`
- `rescue` → `lightcoral`
- `transport` → `lightpink`

### 4. CommandService（命令服务）

**文件：** `command_service.py`

**作用：** 处理用户命令的解析和发送。

**主要功能：**
- 解析用户输入的文本指令
- 将指令转换为标准命令格式
- 发送命令到后端
- 获取命令相关选项（模板、任务ID、命令选项）

**关键方法：**
- `send_user_command(instruction_text)` - 发送用户指令
- `get_task_templates()` - 获取任务模板列表
- `get_task_ids()` - 获取任务ID列表
- `get_command_options()` - 获取命令选项列表

**命令类型识别：**
系统会根据指令文本自动识别命令类型：
- 包含"开始"、"start"、"执行"、"execute" → `start`
- 包含"停止"、"stop"、"暂停"、"pause" → `stop`
- 包含"更新"、"update"、"修改"、"modify" → `update`
- 包含"删除"、"delete"、"移除"、"remove" → `delete`

**命令数据格式：**
```python
{
    "type": "user_command",  # 命令类型
    "instruction": "用户输入的原始文本",
    "timestamp": "2024-01-01T12:00:00",  # ISO格式时间戳
    "source": "gui"
}
```

### 5. SimulationService（仿真服务）

**文件：** `simulation_service.py`

**作用：** 处理仿真场景数据的转换。

**主要功能：**
- 转换智能体数据（位置、颜色、符号）
- 转换目标数据（位置、颜色、激活状态）
- 转换区域数据（圆形、多边形）
- 转换轨迹数据

**关键方法：**
- `get_scene_data_for_gui(timestamp)` - 获取场景数据

**场景数据格式：**
```python
{
    "agents": [
        {
            "id": 1,
            "x": 20.0,
            "y": 30.0,
            "color": "#FF5555",
            "symbol": "o"  # pyqtgraph支持的符号：'o', 's', 't', 'd', '+'
        }
    ],
    "targets": [
        {
            "x": 30.0,
            "y": 40.0,
            "color": "#223399",
            "active": True
        }
    ],
    "regions": [
        {
            "type": "circle",
            "center": (35, 45),
            "radius": 8,
            "color": "#AAAAAA"
        },
        {
            "type": "polygon",
            "points": [(60, 70), (80, 70), (80, 90), (60, 90)],
            "color": "#DDD700"
        }
    ],
    "trajectories": [
        {
            "points": [[10, 20], [15, 25], [20, 30]],
            "color": "#BB5555"
        }
    ],
    "time": 12.5,
    "limits": {
        "x_min": 0,
        "x_max": 100,
        "y_min": 0,
        "y_max": 100
    }
}
```

## 设计模式

### 1. 适配器模式

服务层作为适配器，将不同后端的数据格式转换为GUI统一的格式。这样UI层不需要关心后端的具体实现。

### 2. 依赖注入

所有服务类都通过构造函数接收`BackendAdapter`实例，实现了依赖注入，提高了代码的可测试性和灵活性。

### 3. 单一职责原则

每个服务类只负责一个领域的数据转换：
- `AgentService` - 只处理智能体相关数据
- `TaskService` - 只处理任务相关数据
- `CommandService` - 只处理命令相关逻辑
- `SimulationService` - 只处理仿真场景数据

## 扩展指南

### 添加新的服务

1. 在`services/`目录下创建新的服务文件
2. 在服务类中注入`BackendAdapter`
3. 实现数据转换方法，返回GUI需要的格式
4. 在`services/__init__.py`中导出新服务

### 修改数据格式

如果需要修改GUI数据格式：
1. 修改对应的Service类中的转换方法
2. 确保UI组件能够处理新的数据格式
3. 更新相关文档

### 实现自定义后端

参考`example_backend_adapter.py`，实现`BackendAdapter`的所有抽象方法。确保返回的数据格式符合Service层的期望。

## 注意事项

1. **数据格式一致性**：Service层返回的数据格式必须与UI组件期望的格式一致
2. **错误处理**：Service层应该处理后端数据缺失或格式异常的情况
3. **性能考虑**：数据转换操作应该高效，避免阻塞UI线程
4. **状态映射**：后端状态到中文显示的映射在Service层完成，保持UI层简洁

