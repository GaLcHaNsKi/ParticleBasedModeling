# Particle Viewer MVP

Небольшое desktop-приложение на PySide6 для realtime-визуализации движения частиц в двумерных полях скоростей.

## Что перенесено из текущего проекта

- Обозначения: `q = (x, y)`, `v = (v_x, v_y)`, `u(x, y)`, `Re`, `C_d`.
- Физические константы из `constants.cpp` и `particle.cpp`.
- Все 10 полей скорости из `constants.cpp`.
- Формула Айрова-Тодеса для коэффициента сопротивления:

$$
C_d = \left(0.325 + \sqrt{0.124 + \frac{24}{Re}}\right)^2
$$

- Интегрирование методом Рунге-Кутты 4-го порядка для системы

$$
\dot q = v,
\qquad
\dot v = K |u-v| (u-v),
\qquad
K = \frac{\pi r^2 C_d \rho}{2m}.
$$

## Возможности MVP

- выбор одного из 10 встроенных полей;
- ввод собственного поля через формулы `u_x(x, y)` и `u_y(x, y)`;
- отрисовка стрелок поля;
- отрисовка streamlines;
- клик по сцене создаёт частицу;
- частицы движутся в realtime и оставляют trail;
- timer-based update loop.

## Запуск

Из корня репозитория:

```bash
python particle_viewer_pyside6/main.py
```

Если нужен offscreen-старт для проверки импорта:

```bash
QT_QPA_PLATFORM=offscreen python particle_viewer_pyside6/main.py
```