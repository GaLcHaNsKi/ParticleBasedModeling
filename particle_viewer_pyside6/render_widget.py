from __future__ import annotations

import math
import time

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from particle import Particle
from vector_field import Vec2, VectorField


class FieldWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(900, 620)
        self.setMouseTracking(True)

        self.field = VectorField("1")
        self.particles: list[Particle] = []
        self.show_arrows = True
        self.show_streamlines = True
        self.show_trails = True
        self.paused = False
        self.streamline_quality = 55

        self.world_rect = QRectF(-30.0, -30.0, 60.0, 60.0)
        self.streamlines: list[list[Vec2]] = []

        self._sim_dt = 1.0 / 120.0
        self._accumulator = 0.0
        self._last_frame_time = time.perf_counter()

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)
        self.timer.start()

        self._rebuild_streamlines()

    def set_field(self, field: VectorField) -> None:
        self.field = field
        self._rebuild_streamlines()
        self.update()

    def clear_particles(self) -> None:
        self.particles.clear()
        self.update()

    def set_show_arrows(self, enabled: bool) -> None:
        self.show_arrows = enabled
        self.update()

    def set_streamline_quality(self, value: int) -> None:
        self.streamline_quality = max(10, min(100, value))
        self._rebuild_streamlines()
        self.update()

    def set_show_streamlines(self, enabled: bool) -> None:
        self.show_streamlines = enabled
        self.update()

    def set_show_trails(self, enabled: bool) -> None:
        self.show_trails = enabled
        self.update()

    def set_paused(self, paused: bool) -> None:
        self.paused = paused

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#f7f5ef"))

        self._draw_background_grid(painter)
        if self.show_streamlines:
            self._draw_streamlines(painter)
        if self.show_arrows:
            self._draw_velocity_arrows(painter)
        if self.show_trails:
            self._draw_trails(painter)
        self._draw_particles(painter)
        self._draw_overlay(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            position = self._screen_to_world(event.position())
            self.particles.append(Particle(q=position))
            self.update()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.update()

    def _tick(self) -> None:
        now = time.perf_counter()
        elapsed = min(now - self._last_frame_time, 0.05)
        self._last_frame_time = now

        if self.paused:
            self.update()
            return

        self._accumulator += elapsed
        simulated_steps = 0
        while self._accumulator >= self._sim_dt and simulated_steps < 6:
            alive_particles: list[Particle] = []
            for particle in self.particles:
                if particle.step(self._sim_dt, self.field):
                    alive_particles.append(particle)
            self.particles = alive_particles
            self._accumulator -= self._sim_dt
            simulated_steps += 1

        self.update()

    def _draw_background_grid(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(QColor("#d7d2c4"))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for coordinate in range(-30, 31, 10):
            start_vertical = self._world_to_screen(Vec2(coordinate, -30.0))
            end_vertical = self._world_to_screen(Vec2(coordinate, 30.0))
            painter.drawLine(start_vertical, end_vertical)

            start_horizontal = self._world_to_screen(Vec2(-30.0, coordinate))
            end_horizontal = self._world_to_screen(Vec2(30.0, coordinate))
            painter.drawLine(start_horizontal, end_horizontal)
        painter.restore()

    def _draw_velocity_arrows(self, painter: QPainter) -> None:
        painter.save()
        arrow_pen = QPen(QColor("#0f766e"), 1.2)
        arrow_pen.setCosmetic(True)
        painter.setPen(arrow_pen)

        sample_columns = 10 + self.streamline_quality // 12
        sample_rows = 7 + self.streamline_quality // 18
        sample_points = self._field_samples(sample_columns, sample_rows, inset=3.8)
        max_speed = max((self.field.velocity(point).length() for point in sample_points), default=1.0)
        min_length = 0.6
        max_length = 2.8

        for point in sample_points:
            velocity = self.field.velocity(point)
            speed = velocity.length()
            if speed < 1e-6 or not velocity.is_finite():
                continue
            normalized_speed = min(speed / max(max_speed, 1e-6), 1.0)
            arrow_length = min_length + normalized_speed * (max_length - min_length)
            head = point + velocity.normalized() * arrow_length
            tail_point = self._world_to_screen(point)
            head_point = self._world_to_screen(head)
            painter.drawLine(tail_point, head_point)
            self._draw_arrow_head(painter, point, head, arrow_size=0.65)
        painter.restore()

    def _draw_streamlines(self, painter: QPainter) -> None:
        painter.save()
        pen = QPen(QColor("#6b7280"), 1.0)
        pen.setCosmetic(True)
        painter.setPen(pen)
        for line in self.streamlines:
            if len(line) < 2:
                continue
            path = QPainterPath()
            path.moveTo(self._world_to_screen(line[0]))
            for point in line[1:]:
                path.lineTo(self._world_to_screen(point))
            painter.drawPath(path)
        painter.restore()

    def _draw_trails(self, painter: QPainter) -> None:
        painter.save()
        for particle in self.particles:
            points = list(particle.trail)
            if len(points) < 2:
                continue
            path = QPainterPath()
            path.moveTo(self._world_to_screen(points[0]))
            for point in points[1:]:
                path.lineTo(self._world_to_screen(point))
            painter.setPen(QPen(QColor("#dc2626"), 1.7))
            painter.drawPath(path)
        painter.restore()

    def _draw_particles(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#111827"))
        for particle in self.particles:
            center = self._world_to_screen(particle.q)
            painter.drawEllipse(center, 4.5, 4.5)
        painter.restore()

    def _draw_overlay(self, painter: QPainter) -> None:
        painter.save()
        painter.setPen(QColor("#111827"))
        text = (
            f"Поле: {self.field.definition().title}    "
            f"Частиц: {len(self.particles)}    "
            f"Интегрирование: RK4, dt = {self._sim_dt:.4f} c    "
            f"Гладкость: {self.streamline_quality}"
        )
        painter.drawText(16, 28, text)
        painter.drawText(16, 48, "ЛКМ: создать частицу")
        painter.restore()

    def _draw_arrow_head(self, painter: QPainter, tail: Vec2, head: Vec2, arrow_size: float = 0.7) -> None:
        head_point = self._world_to_screen(head)

        direction = tail - head
        unit = direction.normalized()
        if unit.length() < 1e-6:
            return
        left = Vec2(unit.x * math.cos(0.5) - unit.y * math.sin(0.5), unit.x * math.sin(0.5) + unit.y * math.cos(0.5))
        right = Vec2(unit.x * math.cos(-0.5) - unit.y * math.sin(-0.5), unit.x * math.sin(-0.5) + unit.y * math.cos(-0.5))
        painter.drawLine(head_point, self._world_to_screen(head + left * arrow_size))
        painter.drawLine(head_point, self._world_to_screen(head + right * arrow_size))

    def _rebuild_streamlines(self) -> None:
        self.streamlines.clear()
        columns = 7 + self.streamline_quality // 10
        rows = 5 + self.streamline_quality // 14
        seeds = self._field_samples(columns, rows, inset=4.0)
        for seed in seeds:
            line = self._trace_streamline(seed)
            if len(line) >= 8:
                self.streamlines.append(line)

    def _trace_streamline(self, seed: Vec2) -> list[Vec2]:
        backward = self._integrate_stream(seed, direction=-1.0)
        forward = self._integrate_stream(seed, direction=1.0)
        backward.reverse()
        if backward:
            backward.pop()
        return backward + forward

    def _integrate_stream(self, seed: Vec2, direction: float) -> list[Vec2]:
        points = [seed]
        current = seed
        step_size = 1.15 - 0.85 * (self.streamline_quality / 100.0)
        max_steps = 90 + self.streamline_quality * 3
        min_point_spacing = step_size * 0.45

        for _ in range(max_steps):
            next_point = self._stream_rk4_step(current, direction * step_size)
            if next_point is None:
                break
            if (next_point - current).length() < min_point_spacing:
                break
            current = next_point
            if not self.world_rect.contains(current.x, current.y):
                break
            points.append(current)
        return points

    def _stream_rk4_step(self, point: Vec2, step_size: float) -> Vec2 | None:
        k1 = self._stream_direction(point)
        if k1 is None:
            return None
        k2 = self._stream_direction(point + k1 * (step_size * 0.5))
        if k2 is None:
            return None
        k3 = self._stream_direction(point + k2 * (step_size * 0.5))
        if k3 is None:
            return None
        k4 = self._stream_direction(point + k3 * step_size)
        if k4 is None:
            return None
        delta = (k1 + 2.0 * k2 + 2.0 * k3 + k4) * (step_size / 6.0)
        return point + delta

    def _stream_direction(self, point: Vec2) -> Vec2 | None:
        velocity = self.field.velocity(point)
        speed = velocity.length()
        if speed < 1e-6 or not velocity.is_finite():
            return None
        return velocity / speed

    def _field_samples(self, columns: int, rows: int, inset: float = 2.5) -> list[Vec2]:
        x0 = self.world_rect.left() + inset
        x1 = self.world_rect.right() - inset
        y0 = self.world_rect.top() + inset
        y1 = self.world_rect.bottom() - inset
        samples: list[Vec2] = []
        for row in range(rows):
            ratio_y = row / (rows - 1) if rows > 1 else 0.5
            y = y0 + (y1 - y0) * ratio_y
            for column in range(columns):
                ratio_x = column / (columns - 1) if columns > 1 else 0.5
                x = x0 + (x1 - x0) * ratio_x
                samples.append(Vec2(x, y))
        return samples

    def _world_to_screen(self, point: Vec2) -> QPointF:
        width = max(self.width(), 1)
        height = max(self.height(), 1)
        x_ratio = (point.x - self.world_rect.left()) / self.world_rect.width()
        y_ratio = (point.y - self.world_rect.top()) / self.world_rect.height()
        return QPointF(x_ratio * width, height - y_ratio * height)

    def _screen_to_world(self, point: QPointF) -> Vec2:
        width = max(self.width(), 1)
        height = max(self.height(), 1)
        x = self.world_rect.left() + point.x() / width * self.world_rect.width()
        y = self.world_rect.top() + (height - point.y()) / height * self.world_rect.height()
        return Vec2(x, y)