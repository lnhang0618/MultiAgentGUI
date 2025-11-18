# 中介服务模块 (Services)

中介服务模块定义了统一的后端接口规范，实现UI与后端之间的数据隔离和职责分离。

## 模块概述

中介服务模块采用**接口分离**的设计原则，将后端交互分为两个独立的接口：
1. **DataProvider（数据提供者）**：负责从后端获取数据（后端→UI）
2. **CommandHandler（命令处理器）**：负责处理UI的命令（UI→后端）

`MediatorService`同时实现这两个接口，作为统一的中介服务。

## 核心接口

### DataProvider（数据提供者接口）

负责从后端获取数据并转换为标准格式。

#### 必需方法

- `fetch_agent_data() -> Dict[str, Any]`：获取智能体相关数据
- `fetch_task_data() -> Dict[str, Any]`：获取任务相关数据
- `fetch_simulation_scene(timestamp: float = None) -> Dict[str, Any]`：获取仿真场景数据
- `get_task_templates() -> List[str]`：获取任务模板列表
- `get_task_ids() -> List[str]`：获取当前任务ID列表
- `get_command_options() -> List[str]`：获取可用的命令选项列表

#### 可选方法

- `get_task_template_content(template_name: str) -> str`：获取任务模板的详细内容
- `is_simulation_running() -> bool`：检查仿真是否正在运行
- `step_simulation() -> bool`：推进仿真一个时间步
- `get_current_time() -> float`：获取当前仿真时间

### CommandHandler（命令处理器接口）

负责接收UI的命令并发送到后端。

#### 必需方法

- `receive_command(command_data: Dict[str, Any]) -> bool`：接收UI的命令并发送到后端

### MediatorService（中介服务接口）

同时实现`DataProvider`和`CommandHandler`接口，作为统一的中介服务。

## 数据格式规范

### Agent数据格式

```python
{
    'coalitions': [
        {
            'id': int,                    # 子群ID
            'current_task': str,          # 当前任务名称
            'members': List[int],         # 成员ID列表
            'schedule': [                 # 任务日程
                {'start': float, 'end': float, 'task': str, 'color': str},
                ...
            ],
            'replan_schedule': [...]      # 重规划日程（可选）
        },
        ...
    ],
    'agents': [
        {
            'id': int,                    # 智能体ID
            'type': str,                  # 类型（如'侦察型无人机'）
            'coalition_id': int | None,   # 所属子群ID（敌方可能为None）
            'status': str,                # 状态（'idle', 'working', 'charging'等）
            'faction': str,               # 阵营（'红军'/'蓝军'）
            'x': float,                   # X坐标
            'y': float                    # Y坐标
        },
        ...
    ],
    'current_time': float                 # 当前时间戳
}
```

### Task数据格式

```python
{
    'tasks': [
        {
            'id': int,                    # 任务ID
            'type': str,                  # 任务类型（如'patrol', 'surveillance'）
            'area': str,                  # 任务区域
            'coalition_id': int | -1,     # 所属子群ID（-1表示未分配）
            'status': str,                # 状态（'executing', 'pending'等）
            'start_time': float,          # 开始时间
            'duration': float,            # 持续时间
            'ltl': str                    # LTL公式
        },
        ...
    ],
    'ltl_formula': str,                  # 所有任务的组合LTL公式
    'current_time': float                 # 当前时间戳
}
```

### Simulation Scene数据格式

```python
{
    'agents': [
        {
            'id': int,                    # 智能体ID
            'x': float,                   # X坐标
            'y': float,                   # Y坐标
            'color': str,                 # 颜色（十六进制，如'#FF0000'）
            'symbol': str                 # 符号（'o', 's', 't', 'd', '+'等）
        },
        ...
    ],
    'targets': [
        {
            'x': float,                   # X坐标
            'y': float,                   # Y坐标
            'color': str,                 # 颜色
            'active': bool                # 是否激活
        },
        ...
    ],
    'regions': [
        {
            'type': str,                  # 类型（'circle'或'polygon'）
            'color': str,                 # 颜色
            'center': tuple,              # 圆心（circle类型）
            'radius': float,              # 半径（circle类型）
            'points': List[tuple]         # 顶点列表（polygon类型）
        },
        ...
    ],
    'trajectories': [
        {
            'points': List[List[float]],  # 轨迹点列表 [[x1,y1], [x2,y2], ...]
            'color': str                  # 轨迹颜色
        },
        ...
    ],
    'time': float,                        # 当前时间戳
    'limits': {
        'x_min': float,                   # X轴最小值
        'x_max': float,                   # X轴最大值
        'y_min': float,                   # Y轴最小值
        'y_max': float                    # Y轴最大值
    }
}
```

### Command数据格式

#### 创建任务命令

```python
{
    "type": "create_task",
    "instruction": str,          # 任务指令文本
    "template": str | None,      # 任务模板名称（可选）
    "timestamp": str,            # ISO格式时间戳
    "source": "gui"
}
```

#### 更新任务命令

```python
{
    "type": "update_task",
    "task_id": str,              # 任务ID
    "command": str,              # 命令选项（如"暂停任务"、"恢复任务"等）
    "timestamp": str,
    "source": "gui"
}
```

#### 任务重规划命令

```python
{
    "type": "replan",
    "timestamp": str,
    "source": "gui"
}
```

#### 开始仿真命令

```python
{
    "type": "start_simulation",
    "timestamp": str,
    "source": "gui"
}
```

## 实现示例

### 基本实现

```python
from services import MediatorService
from typing import Dict, Any, List

class MyMediatorService(MediatorService):
    def fetch_agent_data(self) -> Dict[str, Any]:
        # 从后端获取数据并转换为标准格式
        return {
            'coalitions': [...],
            'agents': [...],
            'current_time': 0.0
        }
    
    def fetch_task_data(self) -> Dict[str, Any]:
        # 实现任务数据获取
        pass
    
    def fetch_simulation_scene(self, timestamp: float = None) -> Dict[str, Any]:
        # 实现仿真场景数据获取
        pass
    
    def get_task_templates(self) -> List[str]:
        # 返回模板列表
        return ["模板1", "模板2"]
    
    def get_task_ids(self) -> List[str]:
        # 返回任务ID列表
        return ["1", "2", "3"]
    
    def get_command_options(self) -> List[str]:
        # 返回命令选项列表
        return ["暂停", "恢复"]
    
    def receive_command(self, command_data: Dict[str, Any]) -> bool:
        # 处理命令并发送到后端
        print(f"收到命令: {command_data}")
        # 发送到后端...
        return True
```

### REST API实现示例

```python
import requests
from services import MediatorService
from typing import Dict, Any, List

class RestApiMediatorService(MediatorService):
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def fetch_agent_data(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/agents")
        raw_data = response.json()
        # 转换为标准格式
        return self._convert_agent_data(raw_data)
    
    def receive_command(self, command_data: Dict[str, Any]) -> bool:
        response = requests.post(
            f"{self.base_url}/api/commands",
            json=command_data
        )
        return response.status_code == 200
    
    def _convert_agent_data(self, raw_data: Dict) -> Dict[str, Any]:
        # 实现数据格式转换
        pass
```

## 设计原则

### 1. 数据隔离

`DataProvider`和`CommandHandler`接口完全隔离，互不干扰：
- 数据流单向：后端→UI（DataProvider）
- 命令流单向：UI→后端（CommandHandler）
- 两个接口的数据格式独立定义

### 2. 标准化数据格式

所有数据都转换为标准格式，使得：
- UI层不需要了解后端的具体实现
- 后端可以灵活变化，只要实现标准接口
- 不同后端可以无缝切换

### 3. 可选方法

部分方法（如`get_task_template_content`、`is_simulation_running`）提供默认实现，子类可以覆盖以提供更丰富的功能。

### 4. 向后兼容

保留了`BackendAdapter`和`BackendMediator`别名，确保向后兼容。

## 扩展指南

### 添加新的数据获取方法

1. 在`DataProvider`接口中添加新的抽象方法
2. 在`MediatorService`中继承该方法
3. 在所有实现类中实现该方法

### 添加新的命令类型

1. 在`CommandPanel`中添加新的命令处理逻辑
2. 构造符合规范的`command_data`字典
3. 调用`receive_command()`发送命令
4. 后端在`receive_command()`中处理新命令类型

### 实现模板内容获取

覆盖`get_task_template_content()`方法：

```python
def get_task_template_content(self, template_name: str) -> str:
    # 从后端获取模板详细内容
    template_map = {
        "模板1": "详细内容1",
        "模板2": "详细内容2"
    }
    return template_map.get(template_name, template_name)
```

## 注意事项

1. **数据格式一致性**：确保返回的数据格式符合规范
2. **错误处理**：在实现中应该处理网络错误、数据格式错误等异常情况
3. **性能优化**：对于频繁调用的方法，考虑缓存或优化
4. **线程安全**：如果后端操作涉及多线程，确保线程安全

## 参考实现

- `example_mediator_service.py`：提供完整的示例实现，包含模拟数据

