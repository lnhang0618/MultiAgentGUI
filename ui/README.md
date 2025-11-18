# UI设计文件说明

UI目录包含由Qt Designer生成的界面设计文件，这些文件定义了界面的布局和基本结构。

## 模块概述

UI目录中的文件是使用Qt Designer（`.ui`文件）设计后生成的Python代码。这些文件定义了界面的布局、控件位置和基本属性，但不包含业务逻辑。

## 文件说明

### 1. UI_HomeInterface.py

**对应设计文件：** `UI_HomeInterface.ui`（如果存在）

**功能：** 定义主界面的布局结构。

**主要组件：**
- `TaskInfoWidget` - 任务信息面板容器
- `AgentInfoWidget` - 智能体信息面板容器
- `SimulationWidget` - 仿真画布容器
- `CommandWidget` - 命令面板容器

**使用方式：**
```python
from ui.UI_HomeInterface import Ui_HomeInterface
from PyQt5.QtWidgets import QWidget

class HomeInterface(Ui_HomeInterface, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI布局
```

**说明：**
- 这些容器用于放置实际的业务组件
- 布局通过`setupUi`方法自动设置
- 可以在这些容器中添加自定义组件

### 2. UI_CommandInterface.py

**对应设计文件：** `UI_CommandInterface.ui`（如果存在）

**功能：** 定义命令输入界面的布局结构。

**主要组件：**
- `SmoothScrollArea` - 平滑滚动区域
- `RadioButton` - 单选按钮（可能用于语音输入等）
- `RadioInfoBar` - 信息提示栏
- `TextInputEdit` - 文本输入编辑框
- `TaskTemplateComboBox` - 任务模板下拉框
- `UpdateTaskIdComboBox` - 更新任务ID下拉框
- `UpdateTaskCommandComboBox` - 更新任务命令下拉框

**使用方式：**
```python
from ui.UI_CommandInterface import Ui_CommandInterface
from PyQt5.QtWidgets import QWidget

class CommandInterface(Ui_CommandInterface, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI布局
        
        # 访问UI组件
        text = self.TextInputEdit.toPlainText()
        self.TaskTemplateComboBox.addItems(['模板1', '模板2'])
```

**说明：**
- 使用`qfluentwidgets`库的现代化UI组件
- 支持任务模板选择
- 支持任务更新功能
- 提供文本输入和命令发送功能

## Qt Designer工作流

### 1. 设计界面

使用Qt Designer打开或创建`.ui`文件，通过可视化方式设计界面：
- 拖拽控件到界面
- 设置控件属性
- 调整布局

### 2. 生成Python代码

Qt Designer可以生成Python代码，或者使用`pyuic5`工具：

```bash
pyuic5 UI_HomeInterface.ui -o UI_HomeInterface.py
```

### 3. 在代码中使用

生成的UI类通过多重继承的方式使用：

```python
class MyWidget(Ui_MyWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI
```

## 设计原则

### 1. 分离关注点

UI设计文件只负责布局和基本属性，不包含业务逻辑。业务逻辑在对应的业务类中实现。

### 2. 容器化设计

UI文件主要定义容器（Widget），实际的业务组件在运行时动态添加到这些容器中。

### 3. 可维护性

通过Qt Designer可以方便地修改界面布局，无需手动修改代码。

## 修改界面

### 方法1：使用Qt Designer

1. 打开Qt Designer
2. 打开对应的`.ui`文件（如果存在）
3. 修改布局和属性
4. 保存`.ui`文件
5. 重新生成Python代码

### 方法2：直接修改Python代码

如果`.ui`文件不存在，可以直接修改生成的Python代码，但需要注意：
- 保持`setupUi`方法的结构
- 确保控件名称一致
- 修改后可能无法再通过Qt Designer编辑

## 与业务代码的集成

UI设计文件通过多重继承的方式与业务逻辑集成：

```python
# UI设计文件（自动生成）
class Ui_HomeInterface:
    def setupUi(self, HomeInterface):
        # 设置布局和控件
        pass

# 业务代码
class HomeInterface(Ui_HomeInterface, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        
        # 添加业务逻辑
        self.init_services()
        self.init_sub_widgets()
```

## 注意事项

1. **不要直接修改生成的UI代码**：如果使用`.ui`文件，应该修改`.ui`文件后重新生成代码
2. **控件命名规范**：保持控件名称清晰和一致
3. **布局管理**：使用合适的布局管理器（QVBoxLayout、QHBoxLayout等）
4. **样式设置**：样式可以通过代码设置，也可以在Qt Designer中设置
5. **国际化支持**：如果需要多语言支持，考虑使用Qt的翻译机制

## 扩展指南

### 添加新控件

1. 在Qt Designer中添加控件
2. 设置控件名称和属性
3. 重新生成Python代码
4. 在业务代码中使用新控件

### 修改布局

1. 在Qt Designer中调整布局
2. 保存并重新生成代码
3. 测试布局是否正常显示

### 添加新界面

1. 在Qt Designer中创建新的`.ui`文件
2. 设计界面布局
3. 生成Python代码
4. 创建对应的业务类继承UI类

