from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from ui.UI_CommandInterface import Ui_CommandInterface
from typing import List
from services import MediatorService
from qfluentwidgets import FluentIcon as FIF
import datetime

class CommandPanel(Ui_CommandInterface, QWidget):
    """
    命令界面面板
    负责处理用户命令输入和按钮点击事件
    """
    # 定义信号：当命令执行成功需要刷新数据时发出
    command_executed = pyqtSignal()
    
    def __init__(self, mediator: MediatorService, parent=None):
        """
        初始化命令界面
        参数：
            mediator: MediatorService实例（实现CommandHandler接口）
            parent: 父组件
        """
        super().__init__(parent=parent)
        self.setupUi(self)
        
        # 保存MediatorService实例
        self._mediator = mediator
        
        # 标志：是否正在刷新选项（避免刷新时触发自动填入）
        self._is_refreshing_options = False
        
        self.SmoothScrollArea.setStyleSheet("background-color:transparent;")
        self.RadioButton.setIcon(FIF.MICROPHONE)
        self.RadioInfoBar.stop()
        self.TextInputEdit.setPlainText("示例指令...")

        # 清空所有下拉框，等待中介服务提供数据
        self.TaskTemplateComboBox.clear()
        self.UpdateTaskIdComboBox.clear()
        self.UpdateTaskCommandComboBox.clear()
        
        # 连接按钮信号（在内部处理）
        self._connect_buttons()
        
        # 连接模板选择改变信号：当选择模板时自动填入instruction
        self.TaskTemplateComboBox.currentTextChanged.connect(self._on_template_selection_changed)

    def get_new_task_instruction(self) -> str:
        return self.TextInputEdit.toPlainText()

    def clear_new_task_instruction(self):
        self.TextInputEdit.clear()

    def set_task_id_selection_options(self, task_ids: List[str]):
        """设置任务ID选择下拉框的选项，保留当前选中值"""
        # 保存当前选中的值
        current_selection = self.UpdateTaskIdComboBox.currentText()
        
        self.UpdateTaskIdComboBox.clear()
        if task_ids:
            self.UpdateTaskIdComboBox.addItems(task_ids)
            # 如果之前选中的值还在新列表中，恢复选中
            if current_selection and current_selection in task_ids:
                self.UpdateTaskIdComboBox.setCurrentText(current_selection)

    def set_command_selection_options(self, commands: List[str]):
        """设置命令选择下拉框的选项，保留当前选中值"""
        # 保存当前选中的值
        current_selection = self.UpdateTaskCommandComboBox.currentText()
        
        self.UpdateTaskCommandComboBox.clear()
        if commands:
            self.UpdateTaskCommandComboBox.addItems(commands)
            # 如果之前选中的值还在新列表中，恢复选中
            if current_selection and current_selection in commands:
                self.UpdateTaskCommandComboBox.setCurrentText(current_selection)
    
    # 向后兼容的别名
    def set_update_task_options(self, task_ids: List[str]):
        """向后兼容：使用旧方法名"""
        self.set_task_id_selection_options(task_ids)

    def set_update_command_options(self, commands: List[str]):
        """向后兼容：使用旧方法名"""
        self.set_command_selection_options(commands)
    
    def get_update_task_info(self) -> tuple:
        """向后兼容：使用旧方法名"""
        return self.get_selected_task_update_info()

    def set_task_template_options(self, templates: List[str]):
        """设置任务模板选项（由中介服务提供），保留当前选中值"""
        # 设置刷新标志，避免触发自动填入
        self._is_refreshing_options = True
        
        # 保存当前选中的值
        current_selection = self.TaskTemplateComboBox.currentText()
        
        self.TaskTemplateComboBox.clear()
        if templates:  # 如果有模板，添加模板
            self.TaskTemplateComboBox.addItems(templates)
            # 如果之前选中的值还在新列表中，恢复选中
            if current_selection and current_selection in templates:
                self.TaskTemplateComboBox.setCurrentText(current_selection)
        else:  # 如果没有模板，显示提示
            self.TaskTemplateComboBox.addItem("暂无模板")
        
        # 重置刷新标志
        self._is_refreshing_options = False
    
    def get_selected_task_update_info(self) -> tuple:
        """
        获取选中的任务更新信息
        返回：(task_id, command) 元组，如果未选择则返回 (None, None)
        """
        task_id = self.UpdateTaskIdComboBox.currentText()
        command = self.UpdateTaskCommandComboBox.currentText()
        
        # 检查是否有效选择（排除空字符串和"暂无模板"等占位符）
        if not task_id or task_id == "暂无选项":
            task_id = None
        if not command or command == "暂无选项":
            command = None
            
        return (task_id, command)
    
    def get_task_template(self) -> str:
        """
        获取选择的任务模板
        返回：模板名称，如果未选择则返回 None
        """
        template = self.TaskTemplateComboBox.currentText()
        if not template or template == "暂无模板":
            return None
        return template
    
    def _connect_buttons(self):
        """连接按钮信号到处理方法"""
        # 新增任务按钮
        self.SendTaskPushButton.clicked.connect(self._on_create_task_clicked)
        
        # 修改任务按钮
        self.UpdateTaskPushButton.clicked.connect(self._on_update_task_clicked)
        
        # 任务重规划按钮
        self.ActiveReplanPushButton.clicked.connect(self._on_replan_clicked)
        
        # 开始仿真按钮
        self.StartPushButton.clicked.connect(self._on_start_simulation_clicked)
    
    def _on_template_selection_changed(self, template_name: str):
        """处理模板选择改变事件：自动填入instruction"""
        # 如果正在刷新选项，不执行自动填入（避免覆盖用户输入）
        if self._is_refreshing_options:
            return
        
        # 如果选择了有效模板（不是"暂无模板"或空字符串）
        if template_name and template_name != "暂无模板":
            # 从mediator获取模板的详细内容
            template_content = self._mediator.get_task_template_content(template_name)
            # 填入instruction输入框
            self.TextInputEdit.setPlainText(template_content)
    
    def _on_create_task_clicked(self):
        """处理'新增任务'按钮点击"""
        instruction = self.get_new_task_instruction()
        if instruction and instruction.strip():
            template = self.get_task_template()
            command_data = {
                "type": "create_task",
                "instruction": instruction.strip(),
                "template": template,
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "gui"
            }
            success = self._mediator.receive_command(command_data)
            if success:
                self.clear_new_task_instruction()
                # 发出信号通知需要刷新数据
                self.command_executed.emit()
        else:
            print("请输入任务指令")
    
    def _on_update_task_clicked(self):
        """处理'修改任务'按钮点击"""
        task_id, command = self.get_selected_task_update_info()
        if task_id and command:
            command_data = {
                "type": "update_task",
                "task_id": task_id,
                "command": command,
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "gui"
            }
            success = self._mediator.receive_command(command_data)
            if success:
                # 发出信号通知需要刷新数据
                self.command_executed.emit()
        else:
            print("请选择任务ID和命令选项")
    
    def _on_replan_clicked(self):
        """处理'任务重规划'按钮点击"""
        command_data = {
            "type": "replan",
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "gui"
        }
        success = self._mediator.receive_command(command_data)
        if success:
            # 发出信号通知需要刷新数据
            self.command_executed.emit()
    
    def _on_start_simulation_clicked(self):
        """处理'开始仿真'按钮点击"""
        command_data = {
            "type": "start_simulation",
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "gui"
        }
        success = self._mediator.receive_command(command_data)
        if success:
            # 发出信号通知需要刷新数据
            self.command_executed.emit()
