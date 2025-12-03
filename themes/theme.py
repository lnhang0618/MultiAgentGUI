# theme.py
"""
GUI主题配色配置文件
统一管理界面颜色、样式和主题设置
"""

from PyQt5.QtGui import QColor


class Theme:
    """主题配色方案 - 现代专业风格（浅色主题）"""
    
    # ========== 主色调 ==========
    PRIMARY = "#0078d4"          # 微软蓝 - 专业、可信
    PRIMARY_HOVER = "#106ebe"    # 悬停时加深
    PRIMARY_LIGHT = "#deecf9"    # 浅蓝色背景
    
    SECONDARY = "#00bcf2"        # 天蓝色 - 辅助强调
    SECONDARY_HOVER = "#00a8e0"
    
    # ========== 语义化颜色 ==========
    SUCCESS = "#107c10"          # 成功绿
    SUCCESS_LIGHT = "#dff6dd"    # 成功浅绿背景
    
    WARNING = "#ffaa44"          # 警告橙
    WARNING_LIGHT = "#fff4e5"    # 警告浅橙背景
    
    ERROR = "#d13438"            # 错误红
    ERROR_LIGHT = "#fde7e9"      # 错误浅红背景
    
    INFO = "#0078d4"             # 信息蓝
    INFO_LIGHT = "#deecf9"       # 信息浅蓝背景
    
    # ========== 背景色 ==========
    BACKGROUND = "#f5f5f5"       # 主背景 - 浅灰护眼
    CARD_BACKGROUND = "#ffffff"  # 卡片背景 - 白色清晰
    PANEL_BACKGROUND = "#fafafa" # 面板背景 - 稍浅的灰
    
    # ========== 不同面板的背景色（明显不同） ==========
    PANEL_SIMULATION_BG = "#ffffff"      # 仿真面板 - 纯白
    PANEL_SIMULATION_SCENARIO_BG = "#f8f9fa"  # 场景初始化面板 - 浅灰蓝
    PANEL_TASK_BG = "#fff5f5"            # 任务面板 - 极浅粉红
    PANEL_AGENT_BG = "#f0f8ff"           # 智能体面板 - 极浅蓝
    PANEL_COMMAND_BG = "#f5fff5"         # 命令面板 - 极浅绿

    # ========== 各面板对应的 Header 颜色（比主体更深、对比更强） ==========
    # 这里手动指定，保证颜色关系稳定可控
    # 仿真面板：灰阶，再加深边框
    PANEL_SIMULATION_HEADER_BG = "#ebebeb"
    PANEL_SIMULATION_HEADER_BORDER = "#666666"
    
    # 任务面板：粉色系 header 再加深，对比更强
    PANEL_TASK_HEADER_BG = "#ffd6d6"       # 比之前再深一点
    PANEL_TASK_HEADER_BORDER = "#ff4d4d"   # 明显更深的红
    
    # 智能体面板：蓝色系 header 再加深
    PANEL_AGENT_HEADER_BG = "#d6ebff"      # 再略深一档
    PANEL_AGENT_HEADER_BORDER = "#4096ff"  # 更深的蓝
    
    # 命令面板：绿色系 header 再加深
    PANEL_COMMAND_HEADER_BG = "#ddffdd"    # 再略深一档
    PANEL_COMMAND_HEADER_BORDER = "#33c733"  # 更深的绿
    
    # ========== 边框和分隔线 ==========
    BORDER = "#e0e0e0"           # 浅灰边框
    BORDER_LIGHT = "#f0f0f0"     # 更浅的边框
    DIVIDER = "#e8e8e8"          # 分隔线
    
    # ========== 文本颜色 ==========
    TEXT_PRIMARY = "#333333"     # 深灰主文本 - 高对比度
    TEXT_SECIMARY = "#666666"    # 中灰次要文本
    TEXT_DISABLED = "#999999"    # 浅灰禁用文本
    TEXT_PLACEHOLDER = "#b3b3b3" # 占位符文本
    
    # ========== 阴影效果 ==========
    SHADOW_COLOR = QColor(0, 0, 0, 25)      # 轻微阴影 (10% 透明度)
    SHADOW_COLOR_MEDIUM = QColor(0, 0, 0, 40)  # 中等阴影 (16% 透明度)
    SHADOW_COLOR_STRONG = QColor(0, 0, 0, 60)  # 强阴影 (24% 透明度)
    
    SHADOW_BLUR_RADIUS = 8       # 阴影模糊半径
    SHADOW_OFFSET_X = 0           # 阴影X偏移
    SHADOW_OFFSET_Y = 2          # 阴影Y偏移
    
    # ========== 圆角 ==========
    BORDER_RADIUS = 8            # 卡片圆角
    BORDER_RADIUS_SMALL = 4      # 小组件圆角
    
    # ========== 间距 ==========
    SPACING_SMALL = 4            # 小间距
    SPACING_MEDIUM = 8           # 中间距
    SPACING_LARGE = 16           # 大间距
    
    # ========== 仿真视图专用（深色背景） ==========
    SIM_BACKGROUND = "#1e1e1e"   # 仿真视图背景 - 深色便于可视化
    SIM_TEXT = "#cccccc"         # 仿真视图文本 - 浅色
    
    @classmethod
    def get_global_stylesheet(cls) -> str:
        """获取全局样式表"""
        return f"""
        /* 全局样式 */
        QWidget {{
            background-color: {cls.BACKGROUND};
            color: {cls.TEXT_PRIMARY};
            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            font-size: 9pt;
        }}
        
        /* 非header部分的字体调小一号 */
        QWidget:not(PanelHeader) {{
            font-size: 9pt;
        }}
        
        /* 卡片样式 */
        CardWidget {{
            background-color: {cls.CARD_BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: {cls.BORDER_RADIUS}px;
        }}
        
        /* 按钮样式 */
        QPushButton {{
            background-color: {cls.PRIMARY};
            color: white;
            border: none;
            border-radius: {cls.BORDER_RADIUS_SMALL}px;
            padding: 6px 16px;
            font-weight: 500;
            font-size: 9pt;
        }}
        
        QPushButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
        }}
        
        QPushButton:pressed {{
            background-color: {cls.PRIMARY};
        }}
        
        QPushButton:disabled {{
            background-color: {cls.BORDER_LIGHT};
            color: {cls.TEXT_DISABLED};
        }}

        /* 统一的主操作按钮样式（例如：开始仿真 / 确认发送）
           这里做成“高对比度兜底”，确保即使主题主色调整，文字和边框也不会被吃掉。 */
        QPushButton#PrimaryActionButton {{
            background-color: {cls.PRIMARY};
            color: white;  /* 始终使用白色文字，确保和主色背景有足够对比度 */
            border: 1px solid {cls.PANEL_COMMAND_HEADER_BORDER};
            border-radius: {cls.BORDER_RADIUS_SMALL}px;
            padding: 6px 20px;
            font-weight: 600;
            font-size: 10pt;
        }}
        
        QPushButton#PrimaryActionButton:hover {{
            background-color: {cls.PRIMARY_HOVER};
        }}
        
        QPushButton#PrimaryActionButton:disabled {{
            background-color: {cls.BORDER_LIGHT};
            color: {cls.TEXT_DISABLED};
            border: 1px solid {cls.BORDER};
        }}
        
        /* 输入框样式 */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {cls.CARD_BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: {cls.BORDER_RADIUS_SMALL}px;
            padding: 6px 8px;
            color: {cls.TEXT_PRIMARY};
            font-size: 9pt;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {cls.PRIMARY};
            padding: 5px 7px;
        }}
        
        /* 下拉框样式 */
        QComboBox {{
            background-color: {cls.CARD_BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: {cls.BORDER_RADIUS_SMALL}px;
            padding: 6px 8px;
            color: {cls.TEXT_PRIMARY};
            font-size: 9pt;
        }}
        
        QComboBox:hover {{
            border: 1px solid {cls.PRIMARY};
        }}
        
        QComboBox:focus {{
            border: 2px solid {cls.PRIMARY};
            padding: 5px 7px;
        }}
        
        /* 表格样式 */
        QTableWidget {{
            background-color: {cls.CARD_BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: {cls.BORDER_RADIUS}px;
            gridline-color: {cls.BORDER_LIGHT};
            color: {cls.TEXT_PRIMARY};
            font-size: 9pt;
        }}
        
        QTableWidget::item {{
            border: none;
            padding: 4px;
            font-size: 9pt;
        }}
        
        QTableWidget::item:selected {{
            background-color: {cls.PRIMARY_LIGHT};
            color: {cls.TEXT_PRIMARY};
        }}
        
        QHeaderView::section {{
            background-color: {cls.PANEL_BACKGROUND};
            color: {cls.TEXT_PRIMARY};
            border: none;
            border-bottom: 2px solid {cls.BORDER};
            padding: 6px;
            font-weight: 600;
        }}
        
        /* 滚动条样式 */
        QScrollBar:vertical {{
            background-color: {cls.PANEL_BACKGROUND};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.BORDER};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.TEXT_SECIMARY};
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.PANEL_BACKGROUND};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.BORDER};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.TEXT_SECIMARY};
        }}
        
        /* 标签样式 */
        QLabel {{
            color: {cls.TEXT_PRIMARY};
            font-size: 9pt;
        }}
        
        /* 分隔线样式 */
        QFrame[frameShape="5"] {{
            background-color: {cls.DIVIDER};
            max-height: 1px;
        }}
        """
    
    @classmethod
    def get_card_stylesheet(cls) -> str:
        """获取卡片专用样式表"""
        return f"""
        CardWidget {{
            background-color: {cls.CARD_BACKGROUND};
            border: 1px solid {cls.BORDER};
            border-radius: {cls.BORDER_RADIUS}px;
        }}
        """
    
    @classmethod
    def get_simulation_view_stylesheet(cls) -> str:
        """获取仿真视图专用样式表（深色背景）"""
        return f"""
        QWidget {{
            background-color: {cls.SIM_BACKGROUND};
            color: {cls.SIM_TEXT};
        }}
        """

