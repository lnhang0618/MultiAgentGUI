# services/agent_service.py
from typing import List, Dict, Any
from .backend_adapter import BackendAdapter


class AgentService:
    """
    Agent服务层
    具体部分：GUI接口格式转换（写死）
    抽象部分：后端数据获取（委托给BackendAdapter）
    """
    
    def __init__(self, backend: BackendAdapter):
        """
        参数：
            backend: 后端适配器实例
        """
        self._backend = backend
    
    def get_coalition_data_for_gui(self) -> List[List[str]]:
        """
        获取子群数据，转换为GUI需要的格式
        返回：List[List[str]] - 表格数据 [['子群序号', '当前任务', '成员结构'], ...]
        """
        raw_data = self._backend.fetch_agent_data()
        coalitions = raw_data.get('coalitions', [])
        
        table_data = []
        for coalition in coalitions:
            row = [
                str(coalition.get('id', 'N/A')),
                coalition.get('current_task', '空闲'),
                self._format_members(coalition.get('members', []))
            ]
            table_data.append(row)
        
        return table_data
    
    def get_agent_data_for_gui(self) -> List[List[str]]:
        """
        获取无人机数据，转换为GUI需要的格式
        返回：List[List[str]] - 表格数据 [['无人机序号', '类型', '子群序号', '当前状态'], ...]
        """
        raw_data = self._backend.fetch_agent_data()
        agents = raw_data.get('agents', [])
        
        table_data = []
        for agent in agents:
            row = [
                str(agent.get('id', 'N/A')),
                agent.get('type', '未知'),
                str(agent.get('coalition_id', 'N/A')),
                self._format_status(agent.get('status', 'unknown'))
            ]
            table_data.append(row)
        
        return table_data
    
    def get_unit_gantt_data_for_gui(self) -> Dict[str, Any]:
        """
        获取子群甘特图数据，转换为GUI需要的格式
        返回：甘特图数据字典
        {
            "tracks": [
                {
                    "label": "Unit-0",
                    "bars": [...]
                }
            ],
            "current_time": 10
        }
        """
        raw_data = self._backend.fetch_agent_data()
        coalitions = raw_data.get('coalitions', [])
        
        tracks = []
        for coalition in coalitions:
            track = {
                "label": f"Unit-{coalition.get('id', 0)}",
                "bars": self._convert_schedule_to_bars(
                    coalition.get('schedule', []),
                    coalition.get('current_task', None)
                )
            }
            tracks.append(track)
        
        return {
            "tracks": tracks,
            "current_time": raw_data.get('current_time', 0),
            "y_label_fontsize": 10
        }
    
    def get_replan_gantt_options(self) -> List[str]:
        """
        获取重规划甘特图的选项列表
        返回：选项列表，如 ['Unit-0', 'Unit-1']
        """
        raw_data = self._backend.fetch_agent_data()
        coalitions = raw_data.get('coalitions', [])
        return [f"Unit-{c.get('id', i)}" for i, c in enumerate(coalitions)]
    
    def get_replan_gantt_data_for_gui(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有子群的重规划甘特图数据
        返回：字典 {option_key: gantt_data}
        """
        raw_data = self._backend.fetch_agent_data()
        coalitions = raw_data.get('coalitions', [])
        
        result = {}
        for coalition in coalitions:
            option_key = f"Unit-{coalition.get('id', 0)}"
            replan_schedule = coalition.get('replan_schedule', [])
            
            result[option_key] = {
                "tracks": [
                    {
                        "label": option_key,
                        "bars": self._convert_schedule_to_bars(replan_schedule)
                    }
                ],
                "current_time": raw_data.get('current_time', 0),
                "y_label_fontsize": 10
            }
        
        return result
    
    def _format_members(self, members: List) -> str:
        """格式化成员结构字符串"""
        if not members:
            return "0个成员"
        return f"{len(members)}个成员 [{', '.join(str(m) for m in members[:3])}{'...' if len(members) > 3 else ''}]"
    
    def _format_status(self, status: str) -> str:
        """将后端状态转换为中文显示"""
        status_map = {
            'idle': '空闲',
            'working': '工作中',
            'returning': '返航',
            'charging': '充电中',
            'maintenance': '维护中',
            'unknown': '未知'
        }
        return status_map.get(status, status)
    
    def _convert_schedule_to_bars(self, schedule: List[Dict], current_task: str = None) -> List[Dict]:
        """
        将后端日程数据转换为甘特图条形数据
        参数：
            schedule: [{"start": 0, "end": 5, "task": "task1", "color": "blue"}, ...]
            current_task: 当前任务名称
        返回：甘特图条形数据列表
        """
        bars = []
        for item in schedule:
            bars.append({
                "start": item.get('start', 0),
                "duration": item.get('end', 0) - item.get('start', 0),
                "color": item.get('color', 'silver'),
                "text": item.get('task', ''),
                "alpha": 0.8
            })
        
        # 如果没有数据，至少显示一个空闲状态
        if not bars:
            bars.append({
                "start": 0,
                "duration": 10,
                "color": "silver",
                "text": current_task or "idle",
                "alpha": 0.8
            })
        
        return bars

