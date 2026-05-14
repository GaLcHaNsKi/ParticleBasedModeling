from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable


EPSILON = 1e-6
MAX_EXP_ARGUMENT = 700.0


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float

    def is_finite(self) -> bool:
        return math.isfinite(self.x) and math.isfinite(self.y)

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vec2":
        length = self.length()
        if length < EPSILON:
            return Vec2(0.0, 0.0)
        return self / length


@dataclass(frozen=True)
class FieldDefinition:
    key: str
    title: str
    description: str


SAFE_EVAL_GLOBALS = {
    "__builtins__": {},
    "abs": abs,
    "cos": math.cos,
    "exp": lambda value: math.exp(max(-MAX_EXP_ARGUMENT, min(MAX_EXP_ARGUMENT, value))),
    "log": math.log,
    "pi": math.pi,
    "pow": pow,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
}


PRESET_FIELDS: list[FieldDefinition] = [
    FieldDefinition("1", "Поле 1: однородное", "u = (10, 5) м/с"),
    FieldDefinition("2", "Поле 2: переменное 1", "u_x = 5 + y sin(pi y) + exp(-0.1 x), u_y = 8 + 0.3 x sin(pi y)"),
    FieldDefinition("3", "Поле 3: переменное 2", "u_x = x cos(pi y / 2) + y + 5, u_y = 10 sin(pi y / 2)"),
    FieldDefinition("4", "Поле 4: вихревое", "u_x = -sqrt(x^2 + y^2) y, u_y = sqrt(x^2 + y^2) x"),
    FieldDefinition("5", "Поле 5: масштабированное 3", "Растянутая версия поля 3 для области [-30, 30]^2"),
    FieldDefinition("6", "Поле 6: точечный источник", "Радиальное поле с убыванием скорости как 1 / r"),
    FieldDefinition("7", "Поле 7: линейный источник", "u = 0.5 (x, y)"),
    FieldDefinition("8", "Поле 8: постоянное радиальное", "Почти постоянный модуль скорости, направленный от центра"),
    FieldDefinition("9", "Поле 9: радиально-вихревое", "u = 8 e_r + 5 e_theta"),
    FieldDefinition("10", "Поле 10: два источника", "Сумма двух радиальных источников в (-10, 0) и (10, 0)"),
    FieldDefinition("custom", "Пользовательское поле", "Формулы u_x(x, y) и u_y(x, y)"),
]


class VectorField:
    def __init__(self, key: str = "1", custom_ux: str = "10", custom_uy: str = "5") -> None:
        self._compiled_ux: Callable[[float, float], float] | None = None
        self._compiled_uy: Callable[[float, float], float] | None = None
        self._custom_ux = custom_ux
        self._custom_uy = custom_uy
        self.set_field(key, custom_ux, custom_uy)

    @property
    def key(self) -> str:
        return self._key

    @property
    def custom_ux(self) -> str:
        return self._custom_ux

    @property
    def custom_uy(self) -> str:
        return self._custom_uy

    def set_field(self, key: str, custom_ux: str | None = None, custom_uy: str | None = None) -> None:
        if custom_ux is not None:
            self._custom_ux = custom_ux.strip() or "0"
        if custom_uy is not None:
            self._custom_uy = custom_uy.strip() or "0"

        self._key = key
        self._compiled_ux = None
        self._compiled_uy = None

        if key == "custom":
            self._compiled_ux = self._compile_expression(self._custom_ux)
            self._compiled_uy = self._compile_expression(self._custom_uy)

    def definition(self) -> FieldDefinition:
        for item in PRESET_FIELDS:
            if item.key == self._key:
                return item
        return PRESET_FIELDS[0]

    def velocity(self, position: Vec2) -> Vec2:
        x = position.x
        y = position.y

        if self._key == "1":
            return Vec2(10.0, 5.0)
        if self._key == "2":
            return Vec2(5.0 + y * math.sin(math.pi * y) + _safe_exp(-0.1 * x), 8.0 + 0.3 * x * math.sin(math.pi * y))
        if self._key == "3":
            return Vec2(x * math.cos(math.pi * y / 2.0) + y + 5.0, 10.0 * math.sin(math.pi * y / 2.0))
        if self._key == "4":
            radius = math.hypot(x, y)
            return Vec2(-radius * y, radius * x)
        if self._key == "5":
            return Vec2(x / 30.0 * math.cos(y / 30.0 * math.pi / 2.0) + y / 30.0 + 5.0, 10.0 * math.sin(y / 30.0 * math.pi / 2.0))
        if self._key == "6":
            radius = math.hypot(x, y) + EPSILON
            return Vec2(50.0 * x / (radius * radius), 50.0 * y / (radius * radius))
        if self._key == "7":
            return Vec2(0.5 * x, 0.5 * y)
        if self._key == "8":
            radius = math.hypot(x, y) + EPSILON
            return Vec2(10.0 * x / radius, 10.0 * y / radius)
        if self._key == "9":
            radius = math.hypot(x, y) + EPSILON
            return Vec2((8.0 * x - 5.0 * y) / radius, (8.0 * y + 5.0 * x) / radius)
        if self._key == "10":
            source_a = self._source_velocity(x, y, -10.0, 0.0, 40.0)
            source_b = self._source_velocity(x, y, 10.0, 0.0, 40.0)
            return source_a + source_b

        ux = self._compiled_ux(x, y) if self._compiled_ux is not None else 0.0
        uy = self._compiled_uy(x, y) if self._compiled_uy is not None else 0.0
        return Vec2(float(ux), float(uy))

    def _compile_expression(self, expression: str) -> Callable[[float, float], float]:
        code = compile(expression, "<vector-field>", "eval")

        def evaluator(x: float, y: float) -> float:
            return float(eval(code, SAFE_EVAL_GLOBALS, {"x": x, "y": y}))

        return evaluator

    @staticmethod
    def _source_velocity(x: float, y: float, x0: float, y0: float, k: float) -> Vec2:
        dx = x - x0
        dy = y - y0
        radius = math.hypot(dx, dy) + EPSILON
        return Vec2(k * dx / (radius * radius), k * dy / (radius * radius))


def _safe_exp(value: float) -> float:
    return math.exp(max(-MAX_EXP_ARGUMENT, min(MAX_EXP_ARGUMENT, value)))