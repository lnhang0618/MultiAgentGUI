from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from qfluentwidgets import BodyLabel, PlainTextEdit, ComboBox
from datetime import datetime
from typing import Dict, Any

from MultiAgentGUI.components.panel_header import PanelHeader
from MultiAgentGUI.themes import Theme


class CommandPanel(QWidget):
    """
    精简版命令面板，仅提供两行结构：
    - 第一行：输入指令文本（多行文本框）
    - 第二行（横向）：发布指令模板下拉框 + 修改指令模板下拉框 + 确认发送按钮
    不包含原来的语音输入、任务重规划、仿真控制等功能。
    """
    
    # 命令发送信号：当用户点击"确认发送"按钮时发出
    # 信号携带标准化的命令数据字典
    command_sent = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header：复用统一的 PanelHeader 风格
        header = PanelHeader(
            "命令输入",
            bg_color=Theme.PANEL_COMMAND_HEADER_BG,
            border_color=Theme.PANEL_COMMAND_HEADER_BORDER,
            left_bar_color=Theme.PANEL_COMMAND_HEADER_BORDER,
            text_color=Theme.PANEL_COMMAND_HEADER_BORDER,
        )
        root_layout.addWidget(header)

        # 内容区域背景
        content = QWidget()
        content.setStyleSheet(f"background-color: {Theme.PANEL_COMMAND_BG};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
            Theme.SPACING_MEDIUM,
        )
        content_layout.setSpacing(Theme.SPACING_MEDIUM)

        # 第一行：指令输入文本（标签 + 一整行输入框）
        self.input_label = BodyLabel("输入指令文本：")
        self.text_edit = PlainTextEdit()
        # 使用较小的最小高度 + 伸缩因子，而不是固定最大高度，
        # 这样在面板变矮时不会把下面一行完全挤没
        self.text_edit.setMinimumHeight(80)

        # 第一行加入内容布局
        content_layout.addWidget(self.input_label)
        content_layout.addWidget(self.text_edit, 1)

        # 第二行：两个模板和下拉框（横向排布）
        templates_row = QHBoxLayout()
        templates_row.setSpacing(Theme.SPACING_LARGE)

        self.publish_template_label = BodyLabel("发布指令模板：")
        self.publish_template_combo = ComboBox()
        # 给予更宽的宽度区间，减少长文案被截断的情况
        self.publish_template_combo.setMinimumWidth(160)
        self.publish_template_combo.setMaximumWidth(300)

        self.modify_template_label = BodyLabel("修改指令模板：")
        self.modify_template_combo = ComboBox()
        self.modify_template_combo.setMinimumWidth(160)
        self.modify_template_combo.setMaximumWidth(300)

        templates_row.addWidget(self.publish_template_label)
        templates_row.addWidget(self.publish_template_combo)
        templates_row.addSpacing(Theme.SPACING_MEDIUM)
        templates_row.addWidget(self.modify_template_label)
        templates_row.addWidget(self.modify_template_combo)
        templates_row.addStretch(1)

        content_layout.addLayout(templates_row)

        # 第三行：单独的“发送指令”按钮（与主窗口的开始/暂停仿真按钮风格统一）
        self.send_button = QPushButton("确认发送")
        self.send_button.setObjectName("PrimaryActionButton")
        # 适度的最小尺寸，具体外观由全局样式控制
        self.send_button.setMinimumHeight(32)
        self.send_button.setMinimumWidth(120)
        # 尽管理论上全局样式中的 QPushButton#PrimaryActionButton 已经兜底，
        # 但在某些情况下（例如 qfluentwidgets 或系统主题在运行时再次覆盖按钮样式），
        # 仍可能导致文字颜色被改成和背景接近。
        # 这里在这个关键按钮上再做一层局部覆盖，确保文字和边框始终可见。
        self.send_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: 1px solid {Theme.PANEL_COMMAND_HEADER_BORDER};
                border-radius: {Theme.BORDER_RADIUS_SMALL}px;
                padding: 6px 20px;
                font-weight: 600;
                font-size: 10pt;
            }}

            QPushButton:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}

            QPushButton:disabled {{
                background-color: {Theme.BORDER_LIGHT};
                color: {Theme.TEXT_DISABLED};
                border: 1px solid {Theme.BORDER};
            }}
            """
        )

        button_row = QHBoxLayout()
        # 把按钮放在右侧，更符合操作习惯
        button_row.addStretch(1)
        button_row.addWidget(self.send_button)

        content_layout.addLayout(button_row)

        root_layout.addWidget(content)
        
        # 连接发送按钮的点击事件
        self.send_button.clicked.connect(self._on_send_button_clicked)
        
        # 连接模板选择事件：当选择模板时自动填充指令文本
        self.publish_template_combo.currentTextChanged.connect(self._on_publish_template_selected)
        self.modify_template_combo.currentTextChanged.connect(self._on_modify_template_selected)

    def _on_send_button_clicked(self):
        """处理发送按钮点击事件"""
        instruction_text = self.get_instruction_text().strip()
        
        # 如果没有输入指令文本，不发送命令
        if not instruction_text:
            return
        
        # 确定命令类型：如果有选择修改模板，则可能是修改任务；否则默认为创建任务
        # 这里简化处理，统一使用 create_task，具体类型由后端根据指令内容判断
        command_type = "create_task"
        
        # 获取选中的模板（优先使用发布指令模板）
        selected_template = None
        if self.publish_template_combo.currentText():
            selected_template = self.publish_template_combo.currentText()
        elif self.modify_template_combo.currentText():
            selected_template = self.modify_template_combo.currentText()
        
        # 构建标准化的命令数据
        command_data = {
            "type": command_type,
            "instruction": instruction_text,
            "template": selected_template if selected_template else None,
            "timestamp": datetime.now().isoformat(),
            "source": "gui"
        }
        
        # 发送命令信号
        self.command_sent.emit(command_data)
        
        # 发送成功后清空输入框（可选）
        # self.clear_instruction_text()
    
    def _on_publish_template_selected(self, template_name: str):
        """处理发布指令模板选择事件"""
        if template_name:
            # 这里可以自动填充模板内容，但需要从mediator获取模板内容
            # 暂时只记录选择，不自动填充
            pass
    
    def _on_modify_template_selected(self, template_name: str):
        """处理修改指令模板选择事件"""
        if template_name:
            # 这里可以自动填充模板内容，但需要从mediator获取模板内容
            # 暂时只记录选择，不自动填充
            pass

    # --- 对外简单接口（方便以后接入中介服务） ---
    def get_instruction_text(self) -> str:
        """获取当前输入的指令文本"""
        return self.text_edit.toPlainText()

    def set_instruction_text(self, text: str):
        self.text_edit.setPlainText(text or "")

    def clear_instruction_text(self):
        self.text_edit.clear()

    def set_publish_templates(self, templates):
        """设置“发布任务指令模板”下拉选项"""
        self.publish_template_combo.clear()
        if templates:
            self.publish_template_combo.addItems(list(templates))

    def set_modify_templates(self, templates):
        """设置“修改指令模板”下拉选项"""
        self.modify_template_combo.clear()
        if templates:
            self.modify_template_combo.addItems(list(templates))


