from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import math
import random

from vector_field import Vec2, VectorField


RO_AIR = 1.225
MYU = 1.75e-5
RO_PAR = 2500.3
MIN_RADIUS = 0.00005
MAX_TRAIL_POINTS = 240
POSITION_LIMIT = 120.0
VELOCITY_LIMIT = 600.0


@dataclass
class Particle:
    q: Vec2
    v: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    radius: float = field(default_factory=lambda: MIN_RADIUS + random.uniform(0.0, 1e-4))
    trail: deque[Vec2] = field(default_factory=lambda: deque(maxlen=MAX_TRAIL_POINTS))
    reynolds: float = 0.0
    drag_coefficient: float = 0.0
    alive: bool = True

    def __post_init__(self) -> None:
        self.mass = (4.0 / 3.0) * math.pi * self.radius ** 3 * RO_PAR
        self.trail.append(self.q)

    def step(self, dt: float, field: VectorField) -> bool:
        if not self.alive:
            return False

        qx, qy, vx, vy = self._rk4_step(dt, field)
        if not _is_valid_state(qx, qy, vx, vy):
            self.alive = False
            return False

        self.q = Vec2(qx, qy)
        self.v = Vec2(vx, vy)
        self.trail.append(self.q)
        return True

    def _rhs(self, state: tuple[float, float, float, float], field: VectorField) -> tuple[float, float, float, float]:
        qx, qy, vx, vy = state
        local_velocity = field.velocity(Vec2(qx, qy))
        dv = Vec2(local_velocity.x - vx, local_velocity.y - vy)
        norm = max(dv.length(), 1e-9)
        self.reynolds = max((2.0 * RO_AIR * norm * self.radius) / MYU, 1e-9)
        self.drag_coefficient = (0.325 + math.sqrt(0.124 + 24.0 / self.reynolds)) ** 2
        coefficient = math.pi * self.radius * self.radius * self.drag_coefficient * RO_AIR / (2.0 * self.mass)
        ax = coefficient * norm * (local_velocity.x - vx)
        ay = coefficient * norm * (local_velocity.y - vy)
        return (vx, vy, ax, ay)

    def _rk4_step(self, dt: float, field: VectorField) -> tuple[float, float, float, float]:
        state = (self.q.x, self.q.y, self.v.x, self.v.y)
        k1 = self._rhs(state, field)
        k2 = self._rhs(_state_add(state, k1, dt * 0.5), field)
        k3 = self._rhs(_state_add(state, k2, dt * 0.5), field)
        k4 = self._rhs(_state_add(state, k3, dt), field)
        return tuple(
            state[index] + dt * (k1[index] + 2.0 * k2[index] + 2.0 * k3[index] + k4[index]) / 6.0
            for index in range(4)
        )


def _state_add(
    state: tuple[float, float, float, float],
    derivative: tuple[float, float, float, float],
    factor: float,
) -> tuple[float, float, float, float]:
    return tuple(state[index] + factor * derivative[index] for index in range(4))


def _is_valid_state(qx: float, qy: float, vx: float, vy: float) -> bool:
    return (
        math.isfinite(qx)
        and math.isfinite(qy)
        and math.isfinite(vx)
        and math.isfinite(vy)
        and abs(qx) <= POSITION_LIMIT
        and abs(qy) <= POSITION_LIMIT
        and abs(vx) <= VELOCITY_LIMIT
        and abs(vy) <= VELOCITY_LIMIT
    )