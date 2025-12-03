"""
Agent 数据适配器

将 MediatorService.fetch_agent_data() 返回的标准格式数据
转换为 AgentInfoPanel 需要的展示格式。
"""
from typing import List, Dict, Any


class AgentDataAdapter:
    """Agent 数据适配器，负责数据格式转换"""
    
    @staticmethod
    def convert_coalition_table_data(coalitions: List[Dict]) -> List[List[str]]:
        """将子群数据转换为表格格式"""
        table_data = []
        for coalition in coalitions:
            row = [
                str(coalition.get('id', 'N/A')),
                coalition.get('current_task', '空闲'),
                AgentDataAdapter._format_members(coalition.get('members', []))
            ]
            table_data.append(row)
        return table_data
    
    @staticmethod
    def convert_friendly_agent_table_data(agents: List[Dict]) -> List[List[str]]:
        """将己方智能体数据转换为表格格式"""
        table_data = []
        for agent in agents:
            # 只处理己方（红军）智能体
            faction = agent.get('faction', '')
            if faction == '红军':
                row = [
                    str(agent.get('id', 'N/A')),
                    agent.get('type', '未知'),
                    str(agent.get('coalition_id', 'N/A')) if agent.get('coalition_id') is not None else 'N/A',
                    AgentDataAdapter._format_status(agent.get('status', 'unknown'))
                ]
                table_data.append(row)
        return table_data
    
    @staticmethod
    def convert_enemy_agent_table_data(agents: List[Dict]) -> List[List[str]]:
        """将敌方智能体数据转换为表格格式"""
        table_data = []
        for agent in agents:
            # 只处理敌方（蓝军）智能体
            faction = agent.get('faction', '')
            if faction == '蓝军':
                row = [
                    str(agent.get('id', 'N/A')),
                    agent.get('type', '未知'),
                    AgentDataAdapter._format_status(agent.get('status', 'unknown'))
                ]
                table_data.append(row)
        return table_data
    
    @staticmethod
    def convert_unit_gantt_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """将数据转换为子群甘特图格式"""
        coalitions = data.get('coalitions', [])
        tracks = []
        for coalition in coalitions:
            track = {
                "label": f"Unit-{coalition.get('id', 0)}",
                "bars": AgentDataAdapter._convert_schedule_to_bars(
                    coalition.get('schedule', []),
                    coalition.get('current_task', None)
                )
            }
            tracks.append(track)
        
        return {
            "tracks": tracks,
            "current_time": data.get('current_time', 0),
            "y_label_fontsize": 10
        }
    
    @staticmethod
    def convert_replan_gantt_data(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """将数据转换为重规划甘特图格式"""
        coalitions = data.get('coalitions', [])
        result = {}
        for coalition in coalitions:
            option_key = f"Unit-{coalition.get('id', 0)}"
            replan_schedule = coalition.get('replan_schedule', [])
            
            result[option_key] = {
                "tracks": [
                    {
                        "label": option_key,
                        "bars": AgentDataAdapter._convert_schedule_to_bars(replan_schedule)
                    }
                ],
                "current_time": data.get('current_time', 0),
                "y_label_fontsize": 10
            }
        return result
    
    @staticmethod
    def get_replan_options(coalitions: List[Dict]) -> List[str]:
        """获取重规划甘特图的选项列表"""
        return [f"Unit-{c.get('id', i)}" for i, c in enumerate(coalitions)]
    
    @staticmethod
    def _format_members(members: List) -> str:
        """格式化成员结构字符串"""
        if not members:
            return "0个成员"
        return f"{len(members)}个成员 [{', '.join(str(m) for m in members[:3])}{'...' if len(members) > 3 else ''}]"
    
    @staticmethod
    def _format_status(status: str) -> str:
        """将中介服务状态转换为中文显示"""
        status_map = {
            'idle': '空闲',
            'working': '工作中',
            'returning': '返航',
            'charging': '充电中',
            'maintenance': '维护中',
            'unknown': '未知'
        }
        return status_map.get(status, status)
    
    @staticmethod
    def _convert_schedule_to_bars(schedule: List[Dict], current_task: str = None) -> List[Dict]:
        """
        将中介服务日程数据转换为甘特图条形数据
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

