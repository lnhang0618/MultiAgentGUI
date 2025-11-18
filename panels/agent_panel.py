# panels/agent_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from typing import List, Dict, Any
from components.navi_panel import NavigationPanel
from components.generic_tablewidget import GenericTableWidget
from components.generic_ganntwidget import GenericGanttChart
from components.selectorchartwidget import SelectorChartWidget


class AgentInfoPanel(QWidget):
    """
    Agent信息面板
    负责接收后端标准格式数据，转换为GUI组件需要的格式并显示
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.nav = NavigationPanel()
        layout.addWidget(self.nav)

        # 创建通用组件
        self.coalition_table = GenericTableWidget(['子群序号', '当前任务', '成员结构'])
        # 己方智能体表：包含完整信息（编号、类型、子群序号、当前状态）
        self.friendly_agent_table = GenericTableWidget(['智能体编号', '类型', '子群序号', '当前状态'])
        # 敌方智能体表：只包含可获取的信息（编号、类型、当前状态），不包含子群序号
        self.enemy_agent_table = GenericTableWidget(['智能体编号', '类型', '当前状态'])
        self.unit_gantt = GenericGanttChart()
        self.replan_gantt = SelectorChartWidget()  # 用于重规划甘特图

        # 注册页面
        self.nav.add_page(self.coalition_table, "coalitions", "子群信息")
        self.nav.add_page(self.friendly_agent_table, "friendly_agents", "己方智能体")
        self.nav.add_page(self.enemy_agent_table, "enemy_agents", "敌方智能体")
        self.nav.add_page(self.unit_gantt, "unit_gantt", "子群甘特图")
        self.nav.add_page(self.replan_gantt, "replan_gantt", "子群重规划甘特图")

    def load_data(self, data: Dict[str, Any]):
        """
        从中介服务标准格式数据加载Agent数据并显示
        
        参数：
            data: MediatorService.fetch_agent_data()返回的标准格式数据
            {
                'coalitions': [...],
                'agents': [...],
                'current_time': float
            }
        """
        # 转换子群数据
        coalition_data = self._convert_coalition_data(data.get('coalitions', []))
        self.coalition_table.set_table_data(coalition_data)
        
        # 转换己方智能体数据
        friendly_data = self._convert_friendly_agent_data(data.get('agents', []))
        self.friendly_agent_table.set_table_data(friendly_data)
        
        # 转换敌方智能体数据
        enemy_data = self._convert_enemy_agent_data(data.get('agents', []))
        self.enemy_agent_table.set_table_data(enemy_data)
        
        # 转换子群甘特图数据
        unit_gantt_data = self._convert_unit_gantt_data(data)
        self.unit_gantt.update_plot(unit_gantt_data)
        
        # 转换重规划甘特图数据
        replan_options = self._get_replan_options(data.get('coalitions', []))
        self.replan_gantt.set_options(replan_options)
        
        replan_data_map = self._convert_replan_gantt_data(data)
        for option_key, gantt_data in replan_data_map.items():
            self.replan_gantt.set_chart_data_for_option(option_key, gantt_data)
    
    def _convert_coalition_data(self, coalitions: List[Dict]) -> List[List[str]]:
        """将中介服务子群数据转换为GUI表格格式"""
        table_data = []
        for coalition in coalitions:
            row = [
                str(coalition.get('id', 'N/A')),
                coalition.get('current_task', '空闲'),
                self._format_members(coalition.get('members', []))
            ]
            table_data.append(row)
        return table_data
    
    def _convert_friendly_agent_data(self, agents: List[Dict]) -> List[List[str]]:
        """将中介服务己方智能体数据转换为GUI表格格式"""
        table_data = []
        for agent in agents:
            # 只处理己方（红军）智能体
            faction = agent.get('faction', '')
            if faction == '红军':
                row = [
                    str(agent.get('id', 'N/A')),
                    agent.get('type', '未知'),
                    str(agent.get('coalition_id', 'N/A')) if agent.get('coalition_id') is not None else 'N/A',
                    self._format_status(agent.get('status', 'unknown'))
                ]
                table_data.append(row)
        return table_data
    
    def _convert_enemy_agent_data(self, agents: List[Dict]) -> List[List[str]]:
        """将中介服务敌方智能体数据转换为GUI表格格式"""
        table_data = []
        for agent in agents:
            # 只处理敌方（蓝军）智能体
            faction = agent.get('faction', '')
            if faction == '蓝军':
                row = [
                    str(agent.get('id', 'N/A')),
                    agent.get('type', '未知'),
                    self._format_status(agent.get('status', 'unknown'))
                ]
                table_data.append(row)
        return table_data
    
    def _convert_unit_gantt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将中介服务数据转换为子群甘特图格式"""
        coalitions = data.get('coalitions', [])
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
            "current_time": data.get('current_time', 0),
            "y_label_fontsize": 10
        }
    
    def _convert_replan_gantt_data(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """将中介服务数据转换为重规划甘特图格式"""
        coalitions = data.get('coalitions', [])
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
                "current_time": data.get('current_time', 0),
                "y_label_fontsize": 10
            }
        return result
    
    def _get_replan_options(self, coalitions: List[Dict]) -> List[str]:
        """获取重规划甘特图的选项列表"""
        return [f"Unit-{c.get('id', i)}" for i, c in enumerate(coalitions)]
    
    def _format_members(self, members: List) -> str:
        """格式化成员结构字符串"""
        if not members:
            return "0个成员"
        return f"{len(members)}个成员 [{', '.join(str(m) for m in members[:3])}{'...' if len(members) > 3 else ''}]"
    
    def _format_status(self, status: str) -> str:
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
    
    def _convert_schedule_to_bars(self, schedule: List[Dict], current_task: str = None) -> List[Dict]:
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

    # 保留向后兼容的接口（直接接收已转换的数据）
    def load_backend_data(self, backend_data: Dict[str, Any]):
        """向后兼容：使用旧方法名"""
        self.load_data(backend_data)
    
    def set_agent_data_from_backend(self, backend_data: Dict[str, Any]):
        """向后兼容：使用旧方法名"""
        self.load_data(backend_data)
    
    def set_coalition_data(self, data): 
        """向后兼容：直接设置已转换的子群数据"""
        self.coalition_table.set_table_data(data)

    def set_friendly_agent_data(self, data): 
        """向后兼容：直接设置已转换的己方智能体数据"""
        self.friendly_agent_table.set_table_data(data)
    
    def set_enemy_agent_data(self, data): 
        """向后兼容：直接设置已转换的敌方智能体数据"""
        self.enemy_agent_table.set_table_data(data)

    def set_unit_gantt_data(self, data): 
        """向后兼容：直接设置已转换的子群甘特图数据"""
        self.unit_gantt.update_plot(data)

    def set_replan_gantt_options(self, options): 
        """向后兼容：直接设置重规划甘特图选项"""
        self.replan_gantt.set_options(options)

    def set_replan_gantt_data(self, option_key, data): 
        """向后兼容：直接设置重规划甘特图数据"""
        self.replan_gantt.set_chart_data_for_option(option_key, data)
