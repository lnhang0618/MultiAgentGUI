from PyQt5.QtWidgets import QWidget
from ui.UI_CommandInterface import Ui_CommandInterface
from typing import List
from qfluentwidgets import FluentIcon as FIF

class CommandInterface(Ui_CommandInterface, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        
        self.SmoothScrollArea.setStyleSheet("background-color:transparent;")
        self.RadioButton.setIcon(FIF.MICROPHONE)
        self.RadioInfoBar.stop()
        self.TextInputEdit.setPlainText("示例指令...")

        # 清空所有下拉框，等待后端提供数据
        self.TaskTemplateComboBox.clear()
        self.UpdateTaskIdComboBox.clear()
        self.UpdateTaskCommandComboBox.clear()

    def get_new_task_instruction(self) -> str:
        return self.TextInputEdit.toPlainText()

    def clear_new_task_instruction(self):
        self.TextInputEdit.clear()

    def set_update_task_options(self, task_ids: List[str]):
        self.UpdateTaskIdComboBox.clear()
        self.UpdateTaskIdComboBox.addItems(task_ids)

    def set_update_command_options(self, commands: List[str]):
        self.UpdateTaskCommandComboBox.clear()
        self.UpdateTaskCommandComboBox.addItems(commands)

    def set_task_template_options(self, templates: List[str]):
        """设置任务模板选项（由后端提供）"""
        self.TaskTemplateComboBox.clear()
        if templates:  # 如果有模板，添加模板
            self.TaskTemplateComboBox.addItems(templates)
        else:  # 如果没有模板，显示提示
            self.TaskTemplateComboBox.addItem("暂无模板")