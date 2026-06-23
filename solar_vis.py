# coding: utf-8
# license: GPLv3
"""
Модуль визуализации.
Нигде, кроме этого модуля, не используются экранные координаты объектов.
Функции, создающие графические объекты и перемещающие их на экране, принимают
физические координаты.

В рамках Билета №7 модуль дополнительно умеет:
    - отрисовывать спутники (`create_satellite_image`);
    - отрисовывать орбиты планет и включать/выключать их отображение.
"""

from __future__ import annotations

from typing import Iterable

from solar_objects import SpaceObject, Star, Planet, Satellite

header_font = "Arial-16"
"""Шрифт в заголовке"""

window_width = 800
"""Ширина окна"""

window_height = 800
"""Высота окна"""

scale_factor = None
"""Масштабирование экранных координат по отношению к физическим.
Тип: float
Мера: количество пикселей на один метр."""


def calculate_scale_factor(max_distance: float) -> None:
    """Вычисляет значение глобальной переменной **scale_factor** по данной
    характерной длине.
    """
    global scale_factor
    if max_distance == 0:
        max_distance = 1.0
    scale_factor = 0.4 * min(window_height, window_width) / max_distance
    print('Scale factor:', scale_factor)


def scale_x(x: float) -> int:
    """Возвращает экранную **x** координату по **x** координате модели."""
    return int(x * scale_factor) + window_width // 2


def scale_y(y: float) -> int:
    """Возвращает экранную **y** координату по **y** координате модели.
    Направление оси развёрнуто, чтобы у модели ось **y** смотрела вверх
    (в экранных координатах ось Y направлена вниз, поэтому знак меняется).

    Параметры:

    **y** -- y-координата модели.
    """
    return int(-y * scale_factor) + window_height // 2


def create_star_image(space, star: Star) -> None:
    """Создаёт отображаемый объект звезды."""
    x = scale_x(star.x)
    y = scale_y(star.y)
    r = star.R
    star.image = space.create_oval([x - r, y - r], [x + r, y + r],
                                    fill=star.color)


def create_planet_image(space, planet: Planet) -> None:
    """Создаёт отображаемый объект планеты (аналогично звезде)."""
    x = scale_x(planet.x)
    y = scale_y(planet.y)
    r = planet.R
    planet.image = space.create_oval([x - r, y - r], [x + r, y + r],
                                      fill=planet.color)


def create_satellite_image(space, satellite: Satellite) -> None:
    """Создаёт отображаемый объект спутника (аналогично планете)."""
    x = scale_x(satellite.x)
    y = scale_y(satellite.y)
    r = satellite.R
    satellite.image = space.create_oval([x - r, y - r], [x + r, y + r],
                                         fill=satellite.color)


def create_object_image(space, obj: SpaceObject) -> None:
    """Универсальный диспетчер создания графического образа для любого
    типа космического объекта (звезда/планета/спутник).
    """
    if isinstance(obj, Star):
        create_star_image(space, obj)
    elif isinstance(obj, Planet):
        create_planet_image(space, obj)
    elif isinstance(obj, Satellite):
        create_satellite_image(space, obj)
    else:
        raise AssertionError(f"Unknown space object type: {obj!r}")


def create_orbit_image(space, planet: Planet) -> None:
    """Создаёт (изначально скрытое) изображение орбиты планеты в виде
    окружности вокруг её звезды.
    """
    cx = scale_x(planet.star.x) if planet.star else window_width // 2
    cy = scale_y(planet.star.y) if planet.star else window_height // 2
    r = int(planet.orbit_radius * scale_factor)
    planet.orbit_image = space.create_oval(
        [cx - r, cy - r], [cx + r, cy + r],
        outline="gray25", state="hidden", tags="orbit")


def update_object_position(space, body: SpaceObject) -> None:
    """Перемещает отображаемый объект на холсте."""
    x = scale_x(body.x)
    y = scale_y(body.y)
    r = body.R
    if x + r < 0 or x - r > window_width or y + r < 0 or y - r > window_height:
        space.coords(body.image, window_width + r, window_height + r,
                      window_width + 2 * r, window_height + 2 * r)
        return
    space.coords(body.image, x - r, y - r, x + r, y + r)


def update_system_name(space, system_name: str) -> None:
    """Создаёт на холсте текст с названием системы небесных тел."""
    space.create_text(30, 80, tag="header", text=system_name, font=header_font)


def set_orbits_visible(space, visible: bool) -> None:
    """Включает/выключает отображение всех орбит на холсте."""
    state = "normal" if visible else "hidden"
    space.itemconfigure("orbit", state=state)


if __name__ == "__main__":
    print("This module is not for direct call!")