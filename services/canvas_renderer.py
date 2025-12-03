"""
画布绘制器接口（Canvas Renderer Interface）

设计目的：
- 解决 Mediator 直接操作 UI 的职责边界问题
- 允许不同后端实现不同的绘制逻辑
- Controller 负责协调，但不知道具体绘制细节

架构设计：
┌─────────────────────────────────────────────────────────┐
│ Controller (UI 协调层)                                    │
│ ✅ 定义绘制器接口（抽象）                                 │
│ ✅ 获取 Mediator 的绘制器并调用                           │
│ ❌ 不知道具体绘制细节                                     │
└─────────────────────────────────────────────────────────┘
                          ↓ 使用
┌─────────────────────────────────────────────────────────┐
│ CanvasRenderer (绘制器接口)                               │
│ - 定义抽象的绘制方法                                      │
│ - 由 Mediator 实现具体绘制逻辑                            │
└─────────────────────────────────────────────────────────┘
                          ↓ 实现
┌─────────────────────────────────────────────────────────┐
│ Mediator (后端适配层)                                     │
│ ✅ 实现绘制器接口（具体绘制逻辑）                          │
│ ✅ 根据后端数据决定如何绘制                                │
│ ❌ 不直接持有 UI 组件引用                                  │
└─────────────────────────────────────────────────────────┘
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from typing import Any as TypingAny


class CanvasRenderer(ABC):
    """
    画布绘制器接口
    
    职责：
    - 定义抽象的绘制方法
    - 由 Mediator 实现，封装后端特定的绘制逻辑
    - Controller 调用，但不知道具体绘制细节
    
    设计理念：
    - 不同后端可以实现完全不同的绘制逻辑
    - Controller 只需要知道"调用绘制器"，不需要知道"如何绘制"
    - Mediator 负责实现绘制逻辑，但不直接持有 UI 组件
    """
    
    @abstractmethod
    def render_initial_scene(self, canvas: TypingAny, scene_data: Dict[str, Any]) -> None:
        """
        渲染初始场景到画布
        
        参数：
            canvas: 画布组件（GenericSimulationCanvas）
            scene_data: 场景数据（来自 fetch_simulation_scene）
        
        职责：
        - 根据后端数据在画布上绘制初始场景
        - 不同后端可以实现完全不同的绘制逻辑
        """
        pass
    
    @abstractmethod
    def render_scene_update(self, canvas: TypingAny, scene_data: Dict[str, Any]) -> None:
        """
        渲染场景更新到画布
        
        参数：
            canvas: 画布组件
            scene_data: 更新后的场景数据
        
        职责：
        - 根据后端数据更新画布显示
        - 可以增量更新，也可以全量重绘
        """
        pass
    
    @abstractmethod
    def render_background(self, canvas: TypingAny, background_path: Optional[str]) -> None:
        """
        渲染背景图到画布
        
        参数：
            canvas: 画布组件
            background_path: 背景图路径（可选）
        
        职责：
        - 设置或更新画布背景图
        - 不同后端可能有不同的背景图处理方式
        """
        pass
    
    def render_vector_layer(self, canvas: TypingAny, vector_data: Dict[str, Any]) -> None:
        """
        渲染矢量图层到画布（可选方法）
        
        参数：
            canvas: 画布组件
            vector_data: 矢量数据
        
        职责：
        - 在画布上绘制矢量元素（如区域、路径等）
        - 默认实现为空，子类可以覆盖
        """
        pass

