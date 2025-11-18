# services/simulation_service.py
from typing import Dict, Any
from .backend_adapter import BackendAdapter


class SimulationService:
    """
    Simulation服务层
    具体部分：GUI场景数据格式转换（写死）
    抽象部分：后端场景数据获取（委托给BackendAdapter）
    """
    
    def __init__(self, backend: BackendAdapter):
        """
        参数：
            backend: 后端适配器实例
        """
        self._backend = backend
    
    def get_scene_data_for_gui(self, timestamp: float = None) -> Dict[str, Any]:
        """
        获取仿真场景数据，转换为GUI需要的格式
        参数：
            timestamp: 时间戳，None表示当前时间
        返回：场景数据字典
        {
            "agents": [...],
            "targets": [...],
            "regions": [...],
            "trajectories": [...],
            "time": 12.5,
            "limits": {...}
        }
        """
        raw_data = self._backend.fetch_simulation_scene(timestamp)
        
        # 转换Agent数据
        agents = self._convert_agents(raw_data.get('agents', []))
        
        # 转换Target数据
        targets = self._convert_targets(raw_data.get('targets', []))
        
        # 转换Region数据
        regions = self._convert_regions(raw_data.get('regions', []))
        
        # 转换Trajectory数据
        trajectories = self._convert_trajectories(raw_data.get('trajectories', []))
        
        # 获取边界限制
        limits = raw_data.get('limits', {
            'x_min': 0, 'x_max': 100,
            'y_min': 0, 'y_max': 100
        })
        
        return {
            "agents": agents,
            "targets": targets,
            "regions": regions,
            "trajectories": trajectories,
            "time": raw_data.get('time', 0),
            "limits": limits
        }
    
    def _convert_agents(self, agents: list) -> list:
        """转换Agent数据为GUI格式"""
        result = []
        colors = ["#FF5555", "#55FF55", "#5555FF", "#FFFF55", "#FF55FF", "#55FFFF"]
        
        for i, agent in enumerate(agents):
            result.append({
                "id": agent.get('id', i),
                "x": agent.get('x', 0),
                "y": agent.get('y', 0),
                "color": agent.get('color', colors[i % len(colors)]),
                "symbol": agent.get('symbol', 'o')
            })
        
        return result
    
    def _convert_targets(self, targets: list) -> list:
        """转换Target数据为GUI格式"""
        result = []
        
        for target in targets:
            result.append({
                "x": target.get('x', 0),
                "y": target.get('y', 0),
                "color": target.get('color', "#223399"),
                "active": target.get('active', True)
            })
        
        return result
    
    def _convert_regions(self, regions: list) -> list:
        """转换Region数据为GUI格式"""
        result = []
        
        for region in regions:
            region_data = {
                "type": region.get('type', 'circle'),
                "color": region.get('color', "#AAAAAA")
            }
            
            if region_data["type"] == "circle":
                region_data["center"] = tuple(region.get('center', (0, 0)))
                region_data["radius"] = region.get('radius', 10)
            elif region_data["type"] == "polygon":
                region_data["points"] = region.get('points', [])
            
            result.append(region_data)
        
        return result
    
    def _convert_trajectories(self, trajectories: list) -> list:
        """转换Trajectory数据为GUI格式"""
        result = []
        colors = ["#BB5555", "#55BB55", "#5555BB", "#BBBB55"]
        
        for i, traj in enumerate(trajectories):
            result.append({
                "points": traj.get('points', []),
                "color": traj.get('color', colors[i % len(colors)])
            })
        
        return result


