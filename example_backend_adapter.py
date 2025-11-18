# example_backend_adapter.py
"""
示例后端适配器实现（Example Backend Adapter Implementation）

这是一个完整的 BackendAdapter 实现示例，展示了如何：
1. 继承 BackendAdapter 抽象基类
2. 实现所有必需的抽象方法
3. 提供模拟数据用于开发和测试

开发者可以参考此实现，根据实际需求实现自己的后端适配器，例如：
- RestApiBackend: 通过 REST API 连接后端
- DatabaseBackend: 通过数据库连接后端
- WebSocketBackend: 通过 WebSocket 连接后端
等等。

使用方法：
    from example_backend_adapter import ExampleBackendAdapter
    from home_interface import HomeInterface
    
    backend = ExampleBackendAdapter()
    home_interface = HomeInterface(backend=backend)
"""
import random
import math
from typing import Dict, Any, List
from services.backend_adapter import BackendAdapter


class ExampleBackendAdapter(BackendAdapter):
    """
    示例后端适配器实现
    
    这是一个完整的 BackendAdapter 实现示例，提供模拟数据用于可视化测试。
    继承 BackendAdapter，实现了所有抽象方法，可作为开发参考。
    
    注意：这是一个示例实现，实际项目中需要根据真实后端接口进行适配。
    """
    
    def __init__(self):
        """初始化模拟数据"""
        self._current_time = 0.0
        self._simulation_running = False
        
        # 初始化模拟数据
        self._init_mock_data()
    
    def _init_mock_data(self):
        """初始化模拟数据"""
        # 子群数据
        self._coalitions = [
            {
                'id': 0,
                'current_task': '任务1-巡逻',
                'members': [1, 2, 3],
                'schedule': [
                    {'start': 0, 'end': 5, 'task': 'idle', 'color': 'silver'},
                    {'start': 5, 'end': 10, 'task': '任务1-巡逻', 'color': 'lightblue'},
                    {'start': 10, 'end': 15, 'task': '任务2-侦察', 'color': 'lightgreen'},
                ],
                'replan_schedule': [
                    {'start': 0, 'end': 8, 'task': '重规划-任务A', 'color': 'orange'},
                    {'start': 8, 'end': 16, 'task': '重规划-任务B', 'color': 'purple'},
                ]
            },
            {
                'id': 1,
                'current_task': '任务3-搜索',
                'members': [4, 5],
                'schedule': [
                    {'start': 0, 'end': 6, 'task': 'idle', 'color': 'silver'},
                    {'start': 6, 'end': 12, 'task': '任务3-搜索', 'color': 'lightyellow'},
                    {'start': 12, 'end': 18, 'task': '任务4-运输', 'color': 'lightpink'},
                ],
                'replan_schedule': [
                    {'start': 0, 'end': 7, 'task': '重规划-任务C', 'color': 'cyan'},
                    {'start': 7, 'end': 14, 'task': '重规划-任务D', 'color': 'magenta'},
                ]
            },
            {
                'id': 2,
                'current_task': '空闲',
                'members': [6, 7, 8, 9],
                'schedule': [
                    {'start': 0, 'end': 10, 'task': 'idle', 'color': 'silver'},
                ],
                'replan_schedule': [
                    {'start': 0, 'end': 10, 'task': '待命', 'color': 'gray'},
                ]
            }
        ]
        
        # 无人机数据
        self._agents = [
            {'id': 1, 'type': '侦察型无人机', 'coalition_id': 0, 'status': 'working', 'x': 20, 'y': 30},
            {'id': 2, 'type': '攻击型无人机', 'coalition_id': 0, 'status': 'working', 'x': 25, 'y': 35},
            {'id': 3, 'type': '运输型无人机', 'coalition_id': 0, 'status': 'working', 'x': 22, 'y': 32},
            {'id': 4, 'type': '侦察型无人机', 'coalition_id': 1, 'status': 'working', 'x': 60, 'y': 70},
            {'id': 5, 'type': '攻击型无人机', 'coalition_id': 1, 'status': 'working', 'x': 65, 'y': 75},
            {'id': 6, 'type': '侦察型无人机', 'coalition_id': 2, 'status': 'idle', 'x': 40, 'y': 50},
            {'id': 7, 'type': '攻击型无人机', 'coalition_id': 2, 'status': 'idle', 'x': 45, 'y': 55},
            {'id': 8, 'type': '运输型无人机', 'coalition_id': 2, 'status': 'charging', 'x': 50, 'y': 50},
            {'id': 9, 'type': '侦察型无人机', 'coalition_id': 2, 'status': 'idle', 'x': 42, 'y': 52},
        ]
        
        # 任务数据
        self._tasks = [
            {'id': 1, 'type': 'patrol', 'area': 'A1', 'coalition_id': 0, 'status': 'executing', 
             'start_time': 5, 'duration': 5, 'ltl': 'G (p1 -> F p2)'},
            {'id': 2, 'type': 'surveillance', 'area': 'B2', 'coalition_id': 0, 'status': 'pending',
             'start_time': 10, 'duration': 5, 'ltl': 'G (p2 -> X p3)'},
            {'id': 3, 'type': 'search', 'area': 'C3', 'coalition_id': 1, 'status': 'executing',
             'start_time': 6, 'duration': 6, 'ltl': 'F (p4 & p5)'},
            {'id': 4, 'type': 'transport', 'area': 'D4', 'coalition_id': 1, 'status': 'pending',
             'start_time': 12, 'duration': 6, 'ltl': 'G (p6 -> F p7)'},
            {'id': 5, 'type': 'rescue', 'area': 'E5', 'coalition_id': -1, 'status': 'pending',
             'start_time': 0, 'duration': 0, 'ltl': 'G (p8 -> X p9)'},
        ]
        
        # 场景数据
        self._targets = [
            {'id': 1, 'x': 30, 'y': 40, 'active': True},
            {'id': 2, 'x': 70, 'y': 80, 'active': True},
            {'id': 3, 'x': 50, 'y': 60, 'active': False},
        ]
        
        self._regions = [
            {'type': 'circle', 'center': (35, 45), 'radius': 8, 'color': '#AAAAAA'},
            {'type': 'polygon', 'points': [(60, 70), (80, 70), (80, 90), (60, 90)], 'color': '#DDD700'},
            {'type': 'circle', 'center': (45, 55), 'radius': 5, 'color': '#FFAAAA'},
        ]
    
    def fetch_agent_data(self) -> Dict[str, Any]:
        """获取Agent相关数据"""
        # 动态更新Agent位置（模拟移动）
        if self._simulation_running:
            self._update_agent_positions()
        
        return {
            'coalitions': self._coalitions.copy(),
            'agents': self._agents.copy(),
            'current_time': self._current_time
        }
    
    def fetch_task_data(self) -> Dict[str, Any]:
        """获取Task相关数据"""
        # 组合所有任务的LTL公式
        ltl_formula = ' & '.join([f"({task['ltl']})" for task in self._tasks])
        
        return {
            'tasks': self._tasks.copy(),
            'ltl_formula': ltl_formula,
            'current_time': self._current_time
        }
    
    def fetch_simulation_scene(self, timestamp: float = None) -> Dict[str, Any]:
        """获取仿真场景数据"""
        if timestamp is not None:
            self._current_time = timestamp
        
        # 动态更新Agent位置
        if self._simulation_running:
            self._update_agent_positions()
            self._update_trajectories()
        
        # 构建场景数据
        agents = []
        colors = ["#FF5555", "#55FF55", "#5555FF", "#FFFF55", "#FF55FF", "#55FFFF", "#FF8855", "#5588FF", "#88FF55"]
        # pyqtgraph支持的符号：'o'(circle), 's'(square), 't'(triangle), 'd'(diamond), '+'(plus)
        # 注意：避免使用matplotlib风格的符号如'^', 'v', 'D', 'p', '*', 'x'等
        symbols = ['o', 's', 't', 'd', 't', 's', 'o', '+', 'd']
        
        for i, agent in enumerate(self._agents):
            agents.append({
                'id': agent['id'],
                'x': agent['x'],
                'y': agent['y'],
                'color': colors[i % len(colors)],
                'symbol': symbols[i % len(symbols)]
            })
        
        targets = []
        for target in self._targets:
            targets.append({
                'x': target['x'],
                'y': target['y'],
                'color': '#223399',
                'active': target['active']
            })
        
        # 生成轨迹数据（从Agent当前位置到目标）
        trajectories = []
        for i, agent in enumerate(self._agents[:3]):  # 只为前3个Agent生成轨迹
            if agent['status'] == 'working':
                # 找到对应的目标
                target_idx = i % len(self._targets)
                target = self._targets[target_idx]
                
                # 生成轨迹点
                points = self._generate_trajectory_points(
                    (agent['x'], agent['y']),
                    (target['x'], target['y']),
                    10  # 10个点
                )
                trajectories.append({
                    'points': points,
                    'color': colors[i % len(colors)]
                })
        
        return {
            'agents': agents,
            'targets': targets,
            'regions': self._regions.copy(),
            'trajectories': trajectories,
            'time': self._current_time,
            'limits': {
                'x_min': 0,
                'x_max': 100,
                'y_min': 0,
                'y_max': 100
            }
        }
    
    def send_command(self, command_data: Dict[str, Any]) -> bool:
        """发送命令（模拟）"""
        print(f"[ExampleBackendAdapter] 收到命令: {command_data}")
        
        # 模拟命令处理
        command_type = command_data.get('type', 'unknown')
        instruction = command_data.get('instruction', '')
        
        if '开始' in instruction or 'start' in instruction.lower():
            self._simulation_running = True
            print("[ExampleBackendAdapter] 仿真已启动")
        elif '停止' in instruction or 'stop' in instruction.lower():
            self._simulation_running = False
            print("[ExampleBackendAdapter] 仿真已停止")
        
        return True
    
    def get_task_templates(self) -> List[str]:
        """获取任务模板列表"""
        return [
            "标准巡逻任务",
            "区域侦察任务",
            "目标搜索任务",
            "紧急救援任务",
            "物资运输任务"
        ]
    
    def get_task_ids(self) -> List[str]:
        """获取当前任务ID列表"""
        return [str(task['id']) for task in self._tasks]
    
    def get_command_options(self) -> List[str]:
        """获取可用的命令选项列表"""
        return [
            "开始仿真",
            "停止仿真",
            "暂停任务",
            "恢复任务",
            "更新任务优先级",
            "紧急停止"
        ]
    
    def _update_agent_positions(self):
        """更新Agent位置（模拟移动）"""
        for agent in self._agents:
            if agent['status'] == 'working':
                # 向目标移动
                target_idx = agent['id'] % len(self._targets)
                target = self._targets[target_idx]
                
                dx = target['x'] - agent['x']
                dy = target['y'] - agent['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 1.0:  # 如果还没到达
                    # 移动速度
                    speed = 0.5
                    agent['x'] += (dx / distance) * speed
                    agent['y'] += (dy / distance) * speed
                else:
                    agent['status'] = 'idle'
            elif agent['status'] == 'idle' and random.random() < 0.1:
                # 随机移动
                agent['x'] += random.uniform(-2, 2)
                agent['y'] += random.uniform(-2, 2)
                agent['x'] = max(0, min(100, agent['x']))
                agent['y'] = max(0, min(100, agent['y']))
    
    def _update_trajectories(self):
        """更新轨迹（已通过fetch_simulation_scene中的逻辑实现）"""
        pass
    
    def _generate_trajectory_points(self, start: tuple, end: tuple, num_points: int) -> List[List[float]]:
        """生成轨迹点"""
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t
            points.append([x, y])
        return points
    
    def update_time(self, delta: float):
        """更新时间（用于模拟）"""
        self._current_time += delta
    
    def start_simulation(self):
        """启动仿真"""
        self._simulation_running = True
    
    def stop_simulation(self):
        """停止仿真"""
        self._simulation_running = False


