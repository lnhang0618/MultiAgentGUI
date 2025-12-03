# panels/__init__.py
from MultiAgentGUI.panels.task_panel import TaskInfoPanel
from MultiAgentGUI.panels.agent_panel import AgentInfoPanel
from MultiAgentGUI.panels.command_panel import CommandPanel
from MultiAgentGUI.panels.placeholder_panel import PlaceholderPanel
from MultiAgentGUI.panels.simulation_view_panel import SimulationViewPanel
from MultiAgentGUI.panels.simulation_design_panel import SimulationDesignPanel
from MultiAgentGUI.panels.planner_floating_panel import PlannerFloatingPanel

__all__ = [
    'TaskInfoPanel',
    'AgentInfoPanel',
    'CommandPanel',
    'PlaceholderPanel',
    'SimulationViewPanel',
    'SimulationDesignPanel',
    'PlannerFloatingPanel',
]

