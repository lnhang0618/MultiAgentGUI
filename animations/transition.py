from typing import Iterable, Optional

from PyQt5.QtCore import QEasingCurve, QObject, QParallelAnimationGroup, QPropertyAnimation
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect


class FadeTransitionManager(QObject):
    """
    负责统一管理简单的淡入 / 淡出动画。

    设计理念：
    - main_window_new 只负责告诉它：哪些 widget 要显示 / 隐藏
    - 具体怎么做动画（时长、缓动曲线等）都集中在这里，便于后续统一调整
    """

    def __init__(self, parent: Optional[QObject] = None, duration_ms: int = 420):
        super().__init__(parent)
        self._duration = duration_ms
        self._running_group: Optional[QParallelAnimationGroup] = None

    def _ensure_opacity_effect(self, w: QWidget) -> QGraphicsOpacityEffect:
        effect = w.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(effect)
        return effect

    def fade_widgets(
        self,
        to_show: Iterable[QWidget],
        to_hide: Iterable[QWidget],
        finished_callback: Optional[callable] = None,
    ) -> None:
        """
        为一组 widget 做淡入 / 淡出动画。

        - 对 to_hide：1. 确保可见 → 2. 不透明度 1 → 0 → 3. 动画结束时再 setVisible(False)
        - 对 to_show：1. 先 setVisible(True) → 2. 不透明度 0 → 1
        """
        # 如果上一次动画还在跑，先取消掉
        if self._running_group is not None:
            self._running_group.stop()
            self._running_group.deleteLater()
            self._running_group = None

        group = QParallelAnimationGroup(self)

        # 需要在动画结束后再真正隐藏的 widget
        widgets_to_hide_after = []

        for w in to_hide:
            if w is None:
                continue
            w.setVisible(True)
            effect = self._ensure_opacity_effect(w)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(self._duration)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            group.addAnimation(anim)
            widgets_to_hide_after.append(w)

        for w in to_show:
            if w is None:
                continue
            w.setVisible(True)
            effect = self._ensure_opacity_effect(w)
            # 立即把即将显示的 widget 设为透明，再慢慢淡入
            effect.setOpacity(0.0)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(self._duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            group.addAnimation(anim)

        def _on_finished():
            # 动画结束后，真正隐藏需要关闭的 widget，并把其透明度恢复到 1
            for w in widgets_to_hide_after:
                eff = w.graphicsEffect()
                if isinstance(eff, QGraphicsOpacityEffect):
                    eff.setOpacity(1.0)
                w.setVisible(False)

            if finished_callback is not None:
                finished_callback()

            group.deleteLater()
            self._running_group = None

        group.finished.connect(_on_finished)
        self._running_group = group
        group.start()


