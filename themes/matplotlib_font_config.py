# themes/matplotlib_font_config.py
"""
matplotlib中文字体配置工具
用于统一配置所有matplotlib组件使用中文字体（优先SimHei黑体）
"""
import matplotlib
import matplotlib.pyplot as plt


def setup_chinese_font():
    """
    配置matplotlib使用中文字体（优先使用SimHei黑体）

    优先级顺序：
    1. SimHei（黑体）
    2. Microsoft YaHei（微软雅黑）
    3. WenQuanYi Micro Hei（文泉驿微米黑）
    4. STHeiti（华文黑体）
    5. SimSun（宋体）
    6. DejaVu Sans（备用）

    如果没有找到中文字体，使用默认字体，但设置unicode支持以尽量减少问题
    """
    try:
        # 尝试使用的中文字体列表（按优先级）
        chinese_fonts = [
            'SimHei',
            'Microsoft YaHei',
            'WenQuanYi Micro Hei',
            'STHeiti',
            'SimSun',
            'DejaVu Sans',
        ]

        # 获取系统可用的字体列表
        available_fonts = [f.name for f in matplotlib.font_manager.fontManager.ttflist]

        # 找到第一个可用的中文字体
        selected_font = None
        for font_name in chinese_fonts:
            if font_name in available_fonts:
                selected_font = font_name
                break

        if selected_font:
            # 配置matplotlib使用选定的中文字体
            # 将选定的字体添加到字体列表的开头，保留原有字体作为备用
            plt.rcParams['font.sans-serif'] = [selected_font] + plt.rcParams['font.sans-serif']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
            return selected_font

        # 如果没有找到中文字体，使用默认字体，但尝试设置unicode支持
        plt.rcParams['axes.unicode_minus'] = False
        return None
    except Exception:
        # 如果配置字体失败，使用默认设置
        plt.rcParams['axes.unicode_minus'] = False
        return None


