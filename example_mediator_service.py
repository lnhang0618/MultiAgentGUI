# example_mediator_service.py
"""
示例中介服务实现（Example Mediator Service Implementation）

这是一个完整的 MediatorService 实现示例，展示了如何：
1. 继承 MediatorService 抽象基类（同时实现DataProvider和CommandHandler接口）
2. 实现所有必需的抽象方法
3. 提供模拟数据用于开发和测试

开发者可以参考此实现，根据实际需求实现自己的中介服务，例如：
- RestApiMediatorService: 通过 REST API 连接后端
- DatabaseMediatorService: 通过数据库连接后端
- WebSocketMediatorService: 通过 WebSocket 连接后端
等等。

使用方法：
    from example_mediator_service import ExampleMediatorService
    from main_window import MainWindow
    
    mediator = ExampleMediatorService()
    main_window = MainWindow(backend=mediator)
"""
import random
import math
from typing import Dict, Any, List
from services import MediatorService


class ExampleMediatorService(MediatorService):
    """
    示例中介服务实现
    
    这是一个完整的 MediatorService 实现示例，提供模拟数据用于可视化测试。
    继承 MediatorService，同时实现DataProvider和CommandHandler接口，可作为开发参考。
    
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
        
        # 智能体数据：分为己方和敌方两个独立的列表，结构更清晰
        # 己方（红军）智能体：包含完整的子群信息和状态
        self._friendly_agents = [
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
        
        # 敌方（蓝军）智能体：不包含子群信息，状态可能未知或不完整
        self._enemy_agents = [
            {'id': 10, 'type': '侦察型无人机', 'status': 'unknown', 'x': 10, 'y': 10},
            {'id': 11, 'type': '攻击型无人机', 'status': 'unknown', 'x': 15, 'y': 15},
            {'id': 12, 'type': '侦察型无人机', 'status': 'unknown', 'x': 80, 'y': 20},
            {'id': 13, 'type': '攻击型无人机', 'status': 'unknown', 'x': 85, 'y': 25},
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
        """
        获取Agent相关数据
        
        注意：Agent位置的更新在 step_simulation() 中进行，
        这里只负责返回当前时刻的数据，不进行状态更新。
        """
        # 合并己方和敌方智能体数据（为了保持接口兼容性）
        # 添加faction字段以便服务层区分
        all_agents = []
        for agent in self._friendly_agents:
            agent_copy = agent.copy()
            agent_copy['faction'] = '红军'
            all_agents.append(agent_copy)
        for agent in self._enemy_agents:
            agent_copy = agent.copy()
            agent_copy['faction'] = '蓝军'
            agent_copy['coalition_id'] = None  # 敌方没有子群信息
            all_agents.append(agent_copy)
        
        return {
            'coalitions': self._coalitions.copy(),
            'agents': all_agents,
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
        """
        获取仿真场景数据
        
        注意：Agent位置的更新应该在 step_simulation() 中进行，
        这里只负责返回当前时刻的场景数据。
        如果传入timestamp参数，可以查询历史时刻的数据（回放功能）。
        """
        if timestamp is not None:
            # 如果指定了时间戳，可以用于回放历史数据
            # 这里简化处理，直接使用当前时间
            pass
        
        # 注意：Agent位置的更新在 step_simulation() 中完成
        # 这里不需要再次更新，避免重复计算
        
        # 构建场景数据
        agents = []
        
        # 己方（红军）颜色：红色系
        friendly_colors = ["#FF0000", "#FF4444", "#FF6666", "#FF8888", "#FFAAAA", "#FFCCCC"]
        # 敌方（蓝军）颜色：蓝色系
        enemy_colors = ["#0000FF", "#4444FF", "#6666FF", "#8888FF", "#AAAAFF", "#CCCCFF"]
        # pyqtgraph支持的符号：'o'(circle), 's'(square), 't'(triangle), 'd'(diamond), '+'(plus)
        # 注意：避免使用matplotlib风格的符号如'^', 'v', 'D', 'p', '*', 'x'等
        friendly_symbols = ['o', 's', 't', 'd', 's', 'o']
        enemy_symbols = ['+', 'd', 't', 's', 'o', '+']
        
        # 处理己方智能体
        for i, agent in enumerate(self._friendly_agents):
            agents.append({
                'id': agent['id'],
                'x': agent['x'],
                'y': agent['y'],
                'color': friendly_colors[i % len(friendly_colors)],
                'symbol': friendly_symbols[i % len(friendly_symbols)]
            })
        
        # 处理敌方智能体
        for i, agent in enumerate(self._enemy_agents):
            agents.append({
                'id': agent['id'],
                'x': agent['x'],
                'y': agent['y'],
                'color': enemy_colors[i % len(enemy_colors)],
                'symbol': enemy_symbols[i % len(enemy_symbols)]
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
        # 通常只为己方智能体生成轨迹
        trajectories = []
        for i, agent in enumerate(self._friendly_agents):
            if agent['status'] == 'working' and i < 3:  # 只为前3个工作中的己方智能体生成轨迹
                # 找到对应的目标
                target_idx = agent['id'] % len(self._targets)
                target = self._targets[target_idx]
                
                # 生成轨迹点
                points = self._generate_trajectory_points(
                    (agent['x'], agent['y']),
                    (target['x'], target['y']),
                    10  # 10个点
                )
                trajectories.append({
                    'points': points,
                    'color': friendly_colors[i % len(friendly_colors)]
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
    
    def receive_command(self, command_data: Dict[str, Any]) -> bool:
        """接收UI的命令并发送到后端（模拟）"""
        print(f"[ExampleMediatorService] 收到命令: {command_data}")
        
        # 模拟命令处理
        command_type = command_data.get('type', 'unknown')
        instruction = command_data.get('instruction', '')
        
        if '开始' in instruction or 'start' in instruction.lower():
            self._simulation_running = True
            print("[ExampleMediatorService] 仿真已启动")
        elif '停止' in instruction or 'stop' in instruction.lower():
            self._simulation_running = False
            print("[ExampleMediatorService] 仿真已停止")
        
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
    
    def get_task_template_content(self, template_name: str) -> str:
        """获取任务模板的详细内容（instruction文本）"""
        template_contents = {
            "标准巡逻任务": "在指定区域进行标准巡逻任务，确保区域安全。巡逻路径：从起点A到终点B，途经关键检查点C、D、E。",
            "区域侦察任务": "对目标区域进行详细侦察，收集情报信息。侦察范围：坐标(10,20)到(50,60)的矩形区域。",
            "目标搜索任务": "搜索并定位指定目标。目标特征：红色标记，移动速度中等。搜索区域：半径100米范围内。",
            "紧急救援任务": "执行紧急救援任务，前往坐标(30,40)救援被困人员。优先级：高。预计耗时：30分钟。",
            "物资运输任务": "将物资从起点(0,0)运输到终点(100,100)。物资类型：医疗用品。运输方式：无人机运输。"
        }
        # 返回模板内容，如果模板不存在则返回模板名称
        return template_contents.get(template_name, template_name)
    
    def get_task_ids(self) -> List[str]:
        """获取当前任务ID列表"""
        return [str(task['id']) for task in self._tasks]
    
    def get_command_options(self) -> List[str]:
        """获取可用的命令选项列表"""
        return [
            "暂停任务",
            "恢复任务",
            "更新任务优先级",
            "紧急停止"
        ]
    
    def _update_agent_positions(self):
        """更新Agent位置（模拟移动）"""
        # 更新己方智能体位置
        for agent in self._friendly_agents:
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
        
        # 更新敌方智能体位置
        for agent in self._enemy_agents:
            # 敌方智能体：模拟观测到的移动（更随机，速度可能不同）
            # 由于无法获取敌方完整信息，移动模式更不确定
            if random.random() < 0.3:  # 30%概率移动
                # 随机方向移动
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2, 0.8)  # 速度不确定
                agent['x'] += math.cos(angle) * speed
                agent['y'] += math.sin(angle) * speed
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
    
    def is_simulation_running(self) -> bool:
        """检查仿真是否正在运行"""
        return self._simulation_running
    
    def step_simulation(self) -> bool:
        """
        推进仿真一个时间步
        
        注意：时间步长由后端决定，这里使用固定步长0.1秒。
        不同的后端实现可以使用不同的策略（固定步长、自适应步长等）。
        """
        if not self._simulation_running:
            return False
        
        # 固定时间步长：0.1秒
        time_step = 0.1
        self._current_time += time_step
        
        # 更新Agent位置（基于新的时间步）
        self._update_agent_positions()
        
        return True
    
    def get_current_time(self) -> float:
        """获取当前仿真时间"""
        return self._current_time
    
    def start_simulation(self):
        """启动仿真"""
        self._simulation_running = True
    
    def stop_simulation(self):
        """停止仿真"""
        self._simulation_running = False
    
    def update_time(self, delta: float):
        """
        更新时间（已废弃，保留用于向后兼容）
        建议使用 step_simulation() 方法
        """
        self._current_time += delta


