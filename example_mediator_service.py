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
    from main_window_controller import MainWindowController
    
    mediator = ExampleMediatorService()
    controller = MainWindowController(mediator=mediator)
    controller.show()
"""
import random
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from typing import Any as TypingAny

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from MultiAgentGUI.services.mediator_service import MediatorService
from MultiAgentGUI.services.canvas_renderer import CanvasRenderer


class ExampleCanvasRenderer(CanvasRenderer):
    """
    示例绘制器实现
    
    封装 ExampleMediatorService 的绘制逻辑，实现 CanvasRenderer 接口
    """
    
    def __init__(self, mediator: 'ExampleMediatorService'):
        """
        初始化绘制器
        
        参数：
            mediator: ExampleMediatorService 实例，用于获取数据和绘制方法
        """
        self.mediator = mediator
        # 每个 canvas 对应的绘图状态（背景、图层等）
        self._canvas_states: Dict[int, Dict[str, Any]] = {}
    
    def render_initial_scene(self, canvas: TypingAny, scene_data: Dict[str, Any]) -> None:
        """
        渲染初始场景到画布
        
        包括：设置背景图、绘制智能体、目标、区域、轨迹等
        """
        # 初始化画布状态
        state = self._init_canvas_state(canvas)
        
        # 获取场景限制
        limits = scene_data.get("limits", {
            "x_min": self.mediator.SCENE_X_MIN,
            "x_max": self.mediator.SCENE_X_MAX,
            "y_min": self.mediator.SCENE_Y_MIN,
            "y_max": self.mediator.SCENE_Y_MAX,
        })
        
        # 设置背景图
        bg_path = self.mediator._get_background_image_path()
        if bg_path:
            self.render_background(canvas, bg_path)
        
        # 绘制场景数据
        self.render_scene_update(canvas, scene_data)
    
    def render_scene_update(self, canvas: TypingAny, scene_data: Dict[str, Any]) -> None:
        """
        渲染场景更新到画布
        """
        canvas_id = id(canvas)
        if canvas_id not in self._canvas_states:
            # 如果画布状态不存在，先初始化
            state = self._init_canvas_state(canvas)
        else:
            state = self._canvas_states[canvas_id]
        
        # 使用 mediator 的绘制方法
        self.mediator._render_scene_on_canvas(state, scene_data)
    
    def render_background(self, canvas: TypingAny, background_path: Optional[str]) -> None:
        """
        渲染背景图到画布
        """
        if not background_path:
            return
        
        canvas_id = id(canvas)
        if canvas_id not in self._canvas_states:
            state = self._init_canvas_state(canvas)
        else:
            state = self._canvas_states[canvas_id]
        
        # 获取场景限制
        scene_data = self.mediator.fetch_simulation_scene()
        limits = scene_data.get("limits", {
            "x_min": self.mediator.SCENE_X_MIN,
            "x_max": self.mediator.SCENE_X_MAX,
            "y_min": self.mediator.SCENE_Y_MIN,
            "y_max": self.mediator.SCENE_Y_MAX,
        })
        
        # 使用 mediator 的背景设置方法
        self.mediator._set_canvas_background(state, background_path, limits)
    
    def _init_canvas_state(self, canvas: TypingAny, name: str = "") -> Dict[str, Any]:
        """
        初始化单个画布的状态
        
        这是从 ExampleMediatorService 迁移过来的方法
        """
        state = {
            "name": name,
            "canvas": canvas,
            "background": None,
            "agents": pg.ScatterPlotItem(size=12, pxMode=True),
            "targets": pg.ScatterPlotItem(size=10, pxMode=True),
            "regions": [],
            "trajectories": [],
        }
        canvas.addItem(state["agents"])
        canvas.addItem(state["targets"])
        self._canvas_states[id(canvas)] = state
        return state


class ExampleMediatorService(MediatorService):
    """
    示例中介服务实现
    
    这是一个完整的 MediatorService 实现示例，提供模拟数据用于可视化测试。
    继承 MediatorService，同时实现DataProvider和CommandHandler接口，可作为开发参考。
    
    注意：这是一个示例实现，实际项目中需要根据真实后端接口进行适配。
    """
    
    # 场景坐标范围常量（匹配背景图的实际区域）
    SCENE_X_MIN = 0.0
    SCENE_X_MAX = 100.0
    SCENE_Y_MIN = 0.0
    SCENE_Y_MAX = 56.0  # 背景图的实际高度
    
    def __init__(self):
        """初始化模拟数据"""
        super().__init__()  # 调用父类初始化，设置 _ui_callbacks
        self._current_time = 0.0
        self._simulation_running = False

        # 绑定到前端视图的引用（可选，GenericSimulationCanvas 实例）
        self._sim_view_canvas = None
        self._design_canvas = None
        # 每个 canvas 对应的绘图状态（背景、图层等）
        self._canvas_states: Dict[int, Dict[str, Any]] = {}
        
        # 绘制器实例（延迟初始化）
        self._renderer: Optional[ExampleCanvasRenderer] = None
        
        # 初始化模拟数据
        self._init_mock_data()
    
    def get_canvas_renderer(self) -> Optional[CanvasRenderer]:
        """
        获取画布绘制器
        
        返回 ExampleCanvasRenderer 实例，封装后端特定的绘制逻辑
        """
        if self._renderer is None:
            self._renderer = ExampleCanvasRenderer(self)
        return self._renderer
    
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
        # 注意：y 坐标范围限制在 [0, 56] 以匹配背景图区域
        self._friendly_agents = [
            {'id': 1, 'type': '侦察型无人机', 'coalition_id': 0, 'status': 'working', 'x': 20, 'y': 15},
            {'id': 2, 'type': '攻击型无人机', 'coalition_id': 0, 'status': 'working', 'x': 25, 'y': 18},
            {'id': 3, 'type': '运输型无人机', 'coalition_id': 0, 'status': 'working', 'x': 22, 'y': 16},
            {'id': 4, 'type': '侦察型无人机', 'coalition_id': 1, 'status': 'working', 'x': 60, 'y': 35},
            {'id': 5, 'type': '攻击型无人机', 'coalition_id': 1, 'status': 'working', 'x': 65, 'y': 38},
            {'id': 6, 'type': '侦察型无人机', 'coalition_id': 2, 'status': 'idle', 'x': 40, 'y': 25},
            {'id': 7, 'type': '攻击型无人机', 'coalition_id': 2, 'status': 'idle', 'x': 45, 'y': 28},
            {'id': 8, 'type': '运输型无人机', 'coalition_id': 2, 'status': 'charging', 'x': 50, 'y': 25},
            {'id': 9, 'type': '侦察型无人机', 'coalition_id': 2, 'status': 'idle', 'x': 42, 'y': 26},
        ]
        
        # 敌方（蓝军）智能体：不包含子群信息，状态可能未知或不完整
        # 注意：y 坐标范围限制在 [0, 56] 以匹配背景图区域
        self._enemy_agents = [
            {'id': 10, 'type': '侦察型无人机', 'status': 'unknown', 'x': 10, 'y': 5},
            {'id': 11, 'type': '攻击型无人机', 'status': 'unknown', 'x': 15, 'y': 8},
            {'id': 12, 'type': '侦察型无人机', 'status': 'unknown', 'x': 80, 'y': 10},
            {'id': 13, 'type': '攻击型无人机', 'status': 'unknown', 'x': 85, 'y': 12},
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
        # 注意：y 坐标范围限制在 [0, 56] 以匹配背景图区域
        self._targets = [
            {'id': 1, 'x': 30, 'y': 20, 'active': True},
            {'id': 2, 'x': 70, 'y': 40, 'active': True},
            {'id': 3, 'x': 50, 'y': 30, 'active': False},
        ]
        
        # 注意：regions 的 y 坐标范围限制在 [0, 56] 以匹配背景图区域
        self._regions = [
            {'type': 'circle', 'center': (35, 22), 'radius': 8, 'color': '#AAAAAA'},
            {'type': 'polygon', 'points': [(60, 35), (80, 35), (80, 45), (60, 45)], 'color': '#DDD700'},
            {'type': 'circle', 'center': (45, 28), 'radius': 5, 'color': '#FFAAAA'},
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
                'x_min': self.SCENE_X_MIN,
                'x_max': self.SCENE_X_MAX,
                'y_min': self.SCENE_Y_MIN,
                'y_max': self.SCENE_Y_MAX  # 匹配背景图的实际区域高度
            }
        }

    # ---------- 与前端视图的轻量集成（基于 GenericSimulationCanvas） ----------
    def bind_simulation_views(self, simulation_view_panel, simulation_design_panel) -> None:
        """
        绑定前端的仿真视图和场景设计视图。

        - 使用 MultiAgentGUI/test_background/images.jpg 作为示例背景
        - 在两个视图上绘制初始的矢量场景（确保两个画布都被正确初始化）

        改进点：
        1. 添加断言确保两个画布都不为 None
        2. 统一处理两个画布，避免遗漏
        3. 添加调试日志，便于排查问题
        """
        # 获取画布引用，并添加断言确保不为 None
        self._sim_view_canvas = simulation_view_panel.get_canvas()
        self._design_canvas = simulation_design_panel.get_canvas()
        
        # 断言检查：确保两个画布都成功获取
        assert self._sim_view_canvas is not None, \
            "SimulationViewPanel.get_canvas() 返回了 None，请检查面板初始化"
        assert self._design_canvas is not None, \
            "SimulationDesignPanel.get_canvas() 返回了 None，请检查面板初始化"
        
        # 统一处理两个画布：使用列表和循环，确保两个画布都被初始化
        canvases = [
            ("simulation_view", self._sim_view_canvas),
            ("simulation_design", self._design_canvas),
        ]
        
        states = []
        for name, canvas in canvases:
            state = self._init_canvas_state(canvas, name)
            states.append(state)
            print(f"[ExampleMediatorService] 已初始化画布: {name} (id={id(canvas)})")

        # 构造一份当前场景数据，用于初始化 limits 和矢量图
        scene_data = self.fetch_simulation_scene()
        limits = scene_data.get("limits", {
            "x_min": self.SCENE_X_MIN,
            "x_max": self.SCENE_X_MAX,
            "y_min": self.SCENE_Y_MIN,
            "y_max": self.SCENE_Y_MAX,  # 匹配背景图的实际区域高度
        })

        # 获取背景图路径
        bg_path_str = self._get_background_image_path()

        # 统一设置背景图并绘制初始矢量层（确保两个画布都被处理）
        for state in states:
            canvas_name = state.get("name", "unknown")
            try:
                if bg_path_str:
                    self._set_canvas_background(state, bg_path_str, limits)
                    print(f"[ExampleMediatorService] 已设置背景图: {canvas_name}")
                self._render_scene_on_canvas(state, scene_data)
                print(f"[ExampleMediatorService] 已绘制矢量场景: {canvas_name}")
            except Exception as e:
                print(f"[ExampleMediatorService] 警告: 初始化画布 {canvas_name} 时出错: {e}")
                import traceback
                traceback.print_exc()
        
        # 最终验证：确保两个画布的状态都已保存
        assert len(self._canvas_states) == 2, \
            f"预期初始化 2 个画布，但实际只初始化了 {len(self._canvas_states)} 个"
        print(f"[ExampleMediatorService] 绑定完成，共初始化 {len(self._canvas_states)} 个画布")
    
    def _init_canvas_state(self, canvas, name: str = "") -> Dict[str, Any]:
        """
        初始化单个画布的状态（提取为独立方法，便于复用和测试）。
        
        参数:
            canvas: GenericSimulationCanvas 实例
            name: 画布名称（用于调试日志）
        
        返回:
            画布状态字典
        """
        state = {
            "name": name,  # 添加名称便于调试
            "canvas": canvas,
            "background": None,
            "agents": pg.ScatterPlotItem(size=12, pxMode=True),
            "targets": pg.ScatterPlotItem(size=10, pxMode=True),
            "regions": [],      # List[QGraphicsItem]
            "trajectories": [], # List[PlotDataItem]
        }
        canvas.addItem(state["agents"])
        canvas.addItem(state["targets"])
        self._canvas_states[id(canvas)] = state
        return state
    
    def _get_background_image_path(self) -> str:
        """
        获取背景图路径（提取为独立方法，便于修改和测试）。
        
        返回:
            背景图路径字符串，如果文件不存在则返回空字符串
        """
        base_dir = Path(__file__).resolve().parent
        bg_path = base_dir / "test_background" / "images.jpg"
        if bg_path.exists():
            return str(bg_path)
        else:
            print(f"[ExampleMediatorService] 警告: 背景图不存在: {bg_path}")
            return ""

    def handle_design_scene_event(self, event: Dict[str, Any]) -> None:
        """
        处理来自场景视图的交互事件（示例实现：只打印日志）。

        实际项目中，应该在这里根据事件修改后端场景模型，
        然后基于新的场景数据调用 _render_scene_on_canvas 刷新前端。
        """
        print(f"[ExampleMediatorService] 场景交互事件: {event}")
    
    def import_background_file(self, file_path: str) -> None:
        """
        导入背景图文件（数据处理层）。
        
        注意：此方法只负责数据处理，不包含UI操作（如文件对话框）。
        UI操作（文件选择）应由Controller负责。
        
        参数：
            file_path: 背景图文件路径
        """
        if not file_path:
            print("[ExampleMediatorService] 警告: 文件路径为空")
            return
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"[ExampleMediatorService] 警告: 文件不存在: {file_path}")
            return
        
        print(f"[ExampleMediatorService] 导入背景图: {file_path}")
        
        # 更新所有画布的背景图
        scene_data = self.fetch_simulation_scene()
        limits = scene_data.get("limits", {
            "x_min": self.SCENE_X_MIN,
            "x_max": self.SCENE_X_MAX,
            "y_min": self.SCENE_Y_MIN,
            "y_max": self.SCENE_Y_MAX,
        })
        
        # 为所有已绑定的画布设置新背景
        for state in self._canvas_states.values():
            try:
                self._set_canvas_background(state, file_path, limits)
                print(f"[ExampleMediatorService] 已更新画布背景: {state.get('name', 'unknown')}")
            except Exception as e:
                print(f"[ExampleMediatorService] 更新背景图失败: {e}")
    
    def import_vector_file(self, file_path: str) -> None:
        """
        导入矢量图文件（数据处理层）。
        
        注意：此方法只负责数据处理，不包含UI操作（如文件对话框）。
        UI操作（文件选择）应由Controller负责。
        
        参数：
            file_path: 矢量图文件路径（SVG、DXF等）
        """
        if not file_path:
            print("[ExampleMediatorService] 警告: 文件路径为空")
            return
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"[ExampleMediatorService] 警告: 文件不存在: {file_path}")
            return
        
        print(f"[ExampleMediatorService] 导入矢量图: {file_path}")
        
        # 示例实现：解析矢量图文件并添加到场景
        # 这里简化处理，实际项目中需要根据文件格式（SVG、DXF等）进行解析
        file_ext = file_path_obj.suffix.lower()
        
        if file_ext == '.svg':
            # TODO: 解析SVG文件并添加到场景
            print("[ExampleMediatorService] SVG文件解析（待实现）")
            # 示例：可以添加一个区域到场景
            # self._regions.append({...})
        elif file_ext == '.dxf':
            # TODO: 解析DXF文件并添加到场景
            print("[ExampleMediatorService] DXF文件解析（待实现）")
        else:
            print(f"[ExampleMediatorService] 不支持的矢量图格式: {file_ext}")
        
        # 刷新所有画布显示
        scene_data = self.fetch_simulation_scene()
        for state in self._canvas_states.values():
            try:
                self._render_scene_on_canvas(state, scene_data)
            except Exception as e:
                print(f"[ExampleMediatorService] 刷新画布失败: {e}")
    
    def handle_planner_selection(self, faction: str, planner_name: str) -> None:
        """处理规划器选择变化（示例实现：只打印日志）"""
        print(f"[ExampleMediatorService] 规划器选择变化: {faction} = {planner_name}（接口已预留，待实现）")
        # TODO: 实现规划器切换逻辑
    
    def get_planner_options(self) -> tuple:
        """获取可用的规划器选项（示例实现：返回模拟数据）"""
        # 示例：返回模拟的规划器列表
        red_planners = ["规划器A", "规划器B", "规划器C"]
        blue_planners = ["规划器X", "规划器Y", "规划器Z"]
        return (red_planners, blue_planners)

    # ---------- 简单的场景数据刷新示例 ----------
    def refresh_simulation_canvas(self) -> None:
        """示例：从当前仿真状态刷新两个仿真画布。"""
        if self._sim_view_canvas is None or self._design_canvas is None:
            return

        scene = self.fetch_simulation_scene()
        for state in self._canvas_states.values():
            self._render_scene_on_canvas(state, scene)

    # ---------- 画布背景和矢量层绘制实现（示例） ----------
    def _set_canvas_background(
        self,
        state: Dict[str, Any],
        image_path: str,
        limits: Dict[str, float],
    ) -> None:
        """在指定画布上设置背景图，并与逻辑坐标 limits 对齐。"""
        canvas = state["canvas"]
        img = QtGui.QImage(image_path)
        if img.isNull():
            return

        import numpy as np

        ptr = img.bits()
        ptr.setsize(img.byteCount())
        arr = np.array(ptr, dtype=np.uint8).reshape(img.height(), img.width(), 4)

        # 注意：QImage 的内部存储与 pyqtgraph.ImageItem 的期望轴顺序不同，
        # 直接使用会导致显示时顺时针/逆时针旋转 90°。
        # 这里通过 np.rot90 做一次纠正，使可视化方向与原图一致。
        #
        # 如果你发现方向仍然不对，可以把 k 改成 1 或 3，再运行一次观察效果：
        #   - k = -1（或 3）：逆时针旋转 90°
        #   - k = 1：顺时针旋转 90°
        arr = np.rot90(arr, k=-1)

        if state["background"] is None:
            bg_item = pg.ImageItem(arr)
            bg_item.setZValue(-1000)
            canvas.addItem(bg_item)
            state["background"] = bg_item
        else:
            state["background"].setImage(arr)
            bg_item = state["background"]

        x_min = float(limits.get("x_min", 0.0))
        x_max = float(limits.get("x_max", 100.0))
        y_min = float(limits.get("y_min", 0.0))
        y_max = float(limits.get("y_max", 100.0))

        world_w = max(x_max - x_min, 1e-6)
        world_h = max(y_max - y_min, 1e-6)
        img_h, img_w = arr.shape[:2]

        sx = world_w / img_w
        sy = world_h / img_h
        
        # 使用 max 而不是 min，让背景图覆盖整个坐标范围（而不是被压缩）
        # 这样可以确保背景图至少填满整个显示区域，不会变小
        s = max(sx, sy)

        tr = QtGui.QTransform()
        tr.translate(x_min, y_min)
        tr.scale(s, s)
        bg_item.setTransform(tr)

        # 锁定坐标范围并适配视图
        # xMin/xMax/yMin/yMax 限制平移范围，
        # min*/max*Range 进一步限制缩放倍数，避免无限缩小/放大导致“只剩网格什么都看不到”。
        zoom_min_factor = 0.2  # 最多放大到原来的 5 倍（可根据需要调整）
        zoom_max_factor = 1.0  # 最多缩小到刚好能看到完整场景
        canvas.setLimits(
            xMin=x_min,
            xMax=x_max,
            yMin=y_min,
            yMax=y_max,
            minXRange=world_w * zoom_min_factor,
            maxXRange=world_w * zoom_max_factor,
            minYRange=world_h * zoom_min_factor,
            maxYRange=world_h * zoom_max_factor,
        )
        canvas.setXRange(x_min, x_max, padding=0.02)
        canvas.setYRange(y_min, y_max, padding=0.02)

    def _render_scene_on_canvas(self, state: Dict[str, Any], scene: Dict[str, Any]) -> None:
        """
        将标准化场景数据绘制到给定画布的矢量层上。

        注意：这里只是一个示例实现，真实项目中可以替换为自定义的绘制策略。
        """
        canvas = state["canvas"]
        agents_item: pg.ScatterPlotItem = state["agents"]
        targets_item: pg.ScatterPlotItem = state["targets"]
        regions: List[QtWidgets.QGraphicsItem] = state["regions"]
        trajectories: List[pg.PlotDataItem] = state["trajectories"]

        # Agents
        agents = scene.get("agents", [])
        if agents:
            agents_item.setData(
                x=[float(a.get("x", 0.0)) for a in agents],
                y=[float(a.get("y", 0.0)) for a in agents],
                brush=[pg.mkBrush(a.get("color", "#FF0000")) for a in agents],
                symbol=[a.get("symbol", "o") for a in agents],
            )
        else:
            agents_item.clear()

        # Targets（只画 active=True）
        targets_src = scene.get("targets", [])
        targets = [t for t in targets_src if t.get("active", True)]
        if targets:
            targets_item.setData(
                x=[float(t.get("x", 0.0)) for t in targets],
                y=[float(t.get("y", 0.0)) for t in targets],
                brush=[pg.mkBrush(t.get("color", "#223399")) for t in targets],
            )
        else:
            targets_item.clear()

        # Regions：清空旧的重新画
        for item in regions:
            try:
                canvas.removeItem(item)
            except Exception:
                pass
        regions.clear()

        for region in scene.get("regions", []):
            r_type = region.get("type")
            color = region.get("color", "#AAAAAA")
            pen = QtGui.QPen(QColor(color))
            pen.setWidthF(1.0)
            if r_type == "circle":
                cx, cy = region.get("center", (0.0, 0.0))
                radius = float(region.get("radius", 1.0))
                item = QtWidgets.QGraphicsEllipseItem(
                    cx - radius, cy - radius, 2 * radius, 2 * radius
                )
                item.setPen(pen)
                item.setBrush(QBrush(Qt.NoBrush))
                item.setZValue(-500)
                canvas.addItem(item)
                regions.append(item)
            elif r_type == "polygon":
                pts = region.get("points", [])
                if len(pts) >= 3:
                    poly = QtGui.QPolygonF(
                        [QtCore.QPointF(float(x), float(y)) for x, y in pts]
                    )
                    item = QtWidgets.QGraphicsPolygonItem(poly)
                    item.setPen(pen)
                    item.setBrush(QBrush(Qt.NoBrush))
                    item.setZValue(-500)
                    canvas.addItem(item)
                    regions.append(item)

        # Trajectories：清空旧的重新画
        for item in trajectories:
            try:
                canvas.removeItem(item)
            except Exception:
                pass
        trajectories.clear()

        for traj in scene.get("trajectories", []):
            pts = traj.get("points", [])
            if len(pts) < 2:
                continue
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            color = traj.get("color", "#FF0000")
            item = pg.PlotDataItem(
                x=xs,
                y=ys,
                pen=pg.mkPen(color, width=2),
            )
            item.setZValue(-400)
            canvas.addItem(item)
            trajectories.append(item)
    
    def receive_command(self, command_data: Dict[str, Any]) -> bool:
        """接收UI的命令并发送到后端（模拟）"""
        print(f"[ExampleMediatorService] 收到命令: {command_data}")
        
        # 模拟命令处理
        command_type = command_data.get('type', 'unknown')
        instruction = command_data.get('instruction', '')
        
        if '开始' in instruction or 'start' in instruction.lower():
            self._simulation_running = True
            print("[ExampleMediatorService] 仿真已启动")
            
            # 示例：后端自己决定显示成功通知
            self._call_ui_callback(
                'show_notification',
                message="仿真已成功启动",
                notification_type="success",
                duration=3000
            )
        elif '停止' in instruction or 'stop' in instruction.lower():
            self._simulation_running = False
            print("[ExampleMediatorService] 仿真已停止")
            
            # 示例：后端自己决定显示信息通知
            self._call_ui_callback(
                'show_notification',
                message="仿真已停止",
                notification_type="info",
                duration=2000
            )
        elif command_type == 'create_task':
            # 示例：创建任务时显示警告通知
            self._call_ui_callback(
                'show_notification',
                message="任务创建成功，但需要注意资源限制",
                notification_type="warning",
                duration=5000
            )
        
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
    
    def get_task_graph_data(self) -> Dict[str, Any]:
        """
        获取任务图数据（任务之间的逻辑依赖关系）
        
        返回标准化的任务图数据，只包含节点和边的简单结构。
        这里展示一个示例：任务1 -> 任务2，任务2 -> 任务3，任务1 -> 任务4，任务3 -> 任务4。
        """
        # 根据当前任务数据构建节点（只包含id和label）
        nodes = []
        for task in self._tasks:
            task_id = task['id']
            task_type = task.get('type', 'unknown')
            task_type_label = self._get_task_type_label(task_type)
            
            nodes.append({
                'id': task_id,
                'label': f"T{task_id}: {task_type_label}"
            })
        
        # 构建边（任务依赖关系）
        # 示例：
        # - 先后顺序关系（sequence）：任务1 -> 任务2，任务2 -> 任务3，任务3 -> 任务4
        # - 同时关系（parallel）：任务1 和 任务3 需要同时执行
        edges = []
        task_ids = [task['id'] for task in self._tasks]
        
        # 先后顺序关系（有箭头）
        # 任务1 -> 任务2（如果存在）
        if 1 in task_ids and 2 in task_ids:
            edges.append({'source': 1, 'target': 2, 'type': 'sequence'})
        
        # 任务2 -> 任务3（如果存在）
        if 2 in task_ids and 3 in task_ids:
            edges.append({'source': 2, 'target': 3, 'type': 'sequence'})
        
        # 任务3 -> 任务4（如果存在）
        if 3 in task_ids and 4 in task_ids:
            edges.append({'source': 3, 'target': 4, 'type': 'sequence'})
        
        # 同时关系（无箭头虚线）
        # 任务1 和 任务3 需要同时执行（如果存在）
        if 1 in task_ids and 3 in task_ids:
            edges.append({'source': 1, 'target': 3, 'type': 'parallel'})
        
        return {
            'nodes': nodes,
            'edges': edges,
            'layout': {
                'algorithm': 'hierarchical'  # 使用层次布局展示依赖关系
            }
        }
    
    def _get_task_type_label(self, task_type: str) -> str:
        """将任务类型转换为中文标签"""
        type_map = {
            'patrol': '巡逻',
            'surveillance': '侦察',
            'search': '搜索',
            'rescue': '救援',
            'transport': '运输'
        }
        return type_map.get(task_type, task_type)
    
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
                    # 限制在背景图区域内
                    agent['x'] = max(self.SCENE_X_MIN, min(self.SCENE_X_MAX, agent['x']))
                    agent['y'] = max(self.SCENE_Y_MIN, min(self.SCENE_Y_MAX, agent['y']))
                else:
                    agent['status'] = 'idle'
            elif agent['status'] == 'idle' and random.random() < 0.1:
                # 随机移动（限制在背景图区域内）
                agent['x'] += random.uniform(-2, 2)
                agent['y'] += random.uniform(-2, 2)
                agent['x'] = max(self.SCENE_X_MIN, min(self.SCENE_X_MAX, agent['x']))
                agent['y'] = max(self.SCENE_Y_MIN, min(self.SCENE_Y_MAX, agent['y']))
        
        # 更新敌方智能体位置
        for agent in self._enemy_agents:
            # 敌方智能体：模拟观测到的移动（更随机，速度可能不同）
            # 由于无法获取敌方完整信息，移动模式更不确定
            if random.random() < 0.3:  # 30%概率移动
                # 随机方向移动（限制在背景图区域内）
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.2, 0.8)  # 速度不确定
                agent['x'] += math.cos(angle) * speed
                agent['y'] += math.sin(angle) * speed
                agent['x'] = max(self.SCENE_X_MIN, min(self.SCENE_X_MAX, agent['x']))
                agent['y'] = max(self.SCENE_Y_MIN, min(self.SCENE_Y_MAX, agent['y']))
    
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


