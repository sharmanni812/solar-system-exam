# coding: utf-8
# license: GPLv3
"""
Модуль описания космических объектов в парадигме ООП.

Реализован для условий Билета №7:
    - 3 звезды: у 1-й -- 10 планет, у 2-й -- 20 планет, у 3-й -- 10 планет;
    - максимум 4 планеты на одной орбите (у каждой звезды);
    - у всех планет 2-й звезды, расположенных на нечётных орбитах, есть
      по 1 спутнику;
    - планеты на чётных орбитах вращаются по часовой стрелке,
      на нечётных -- против часовой стрелки;
    - планеты разных звёзд не сталкиваются (т.к. их орбиты строятся
      вокруг разных, далеко разнесённых звёзд), орбиты звёзд могут
      пересекаться в проекции на плоскость экрана;
    - спутники не сталкиваются друг с другом и с планетой (разные
      радиусы орбит вокруг планеты).
"""

from __future__ import annotations

import math
from typing import List, Optional


MAX_PLANETS_PER_ORBIT = 4
"""Максимальное количество планет на одной орбите (по условию билета)."""


class SpaceObject:
    """Базовый класс любого космического объекта.

    Хранит общие для всех объектов (звезда/планета/спутник) атрибуты:
    координаты, цвет, экранный радиус и графический образ.
    """

    def __init__(self, R: int, color: str, m: float,
                 x: float = 0.0, y: float = 0.0) -> None:
        self.R: int = R
        """Видимый радиус объекта на экране (в пикселах)."""
        self.color: str = color
        """Цвет объекта."""
        self.m: float = m
        """Масса объекта."""
        self.x: float = x
        """Координата по оси X."""
        self.y: float = y
        """Координата по оси Y."""
        self.image: Optional[int] = None
        """Идентификатор графического образа на холсте tkinter."""
        self.orbit_image: Optional[int] = None
        """Идентификатор изображения орбиты (окружности) на холсте."""

    @property
    def type(self) -> str:
        """Текстовый тип объекта (используется visualization-модулем)."""
        return self.__class__.__name__.lower()

    def step(self, dt: float) -> None:
        """Пересчитать положение объекта за шаг времени dt.

        Переопределяется в наследниках, реализующих собственную
        механику движения (круговая орбита у Planet/Satellite,
        звезда обычно неподвижна).
        """
        raise NotImplementedError


class Star(SpaceObject):
    """Звезда -- центр своей планетной системы. В рамках билета считается
    неподвижной; вокруг неё вращаются Planet-объекты.
    """

    def __init__(self, R: int, color: str, m: float,
                 x: float = 0.0, y: float = 0.0) -> None:
        super().__init__(R, color, m, x, y)
        self.planets: List["Planet"] = []
        """Список планет, принадлежащих данной звезде."""

    def add_planet(self, planet: "Planet") -> None:
        """Привязать планету к звезде (как к центру вращения)."""
        planet.star = self
        self.planets.append(planet)

    def step(self, dt: float) -> None:
        """Звезда в данной модели неподвижна."""
        return

    def populate_orbits(self, planet_count: int,
                         planet_factory) -> List["Planet"]:
        """Создаёт `planet_count` планет данной звезды и расставляет их
        по орбитам не более чем по MAX_PLANETS_PER_ORBIT штук на орбиту.

        Направление вращения планеты определяется чётностью номера
        орбиты (1 -- первая, самая близкая к звезде): чётные орбиты --
        по часовой стрелке, нечётные -- против часовой стрелки.

        Параметры:

        **planet_count** -- сколько планет нужно создать у этой звезды.
        **planet_factory** -- функция (orbit_index, angle0, clockwise) ->
            Planet, создающая planet с нужными параметрами.
        """
        created: List["Planet"] = []
        orbit_index = 1
        placed_in_orbit = 0
        for i in range(planet_count):
            if placed_in_orbit == MAX_PLANETS_PER_ORBIT:
                orbit_index += 1
                placed_in_orbit = 0
            clockwise = (orbit_index % 2 == 0)
            # равномерно распределяем планеты внутри орбиты по углу
            angle0 = 2 * math.pi * placed_in_orbit / MAX_PLANETS_PER_ORBIT
            planet = planet_factory(orbit_index, angle0, clockwise)
            self.add_planet(planet)
            created.append(planet)
            placed_in_orbit += 1
        return created


class Planet(SpaceObject):
    """Планета, вращающаяся вокруг звезды по круговой орбите."""

    BASE_ORBIT_RADIUS = 60.0
    """Радиус первой орбиты (в физических единицах модели)."""
    ORBIT_STEP = 35.0
    """Расстояние между соседними орбитами."""
    ANGULAR_SPEED = 0.6
    """Базовая угловая скорость планеты (рад/с), масштабируется
    по номеру орбиты, чтобы дальние планеты двигались медленнее
    (как в реальности по 3-му закону Кеплера, в упрощённом виде)."""

    def __init__(self, R: int, color: str, m: float,
                 orbit_index: int, angle0: float, clockwise: bool) -> None:
        super().__init__(R, color, m)
        self.star: Optional[Star] = None
        self.orbit_index: int = orbit_index
        """Номер орбиты планеты (1 -- ближайшая к звезде)."""
        self.orbit_radius: float = (self.BASE_ORBIT_RADIUS
                                     + (orbit_index - 1) * self.ORBIT_STEP)
        """Радиус орбиты в физических единицах модели."""
        self.angle: float = angle0
        """Текущий угол положения планеты на орбите (рад)."""
        self.clockwise: bool = clockwise
        """Направление вращения: True -- по часовой стрелке."""
        self.satellites: List["Satellite"] = []
        """Спутники данной планеты (если есть)."""
        self._update_xy()

    def add_satellite(self, satellite: "Satellite") -> None:
        """Привязать спутник к данной планете."""
        satellite.planet = self
        self.satellites.append(satellite)

    def _update_xy(self) -> None:
        """Пересчитать (x, y) планеты по текущему углу и положению звезды."""
        cx = self.star.x if self.star else 0.0
        cy = self.star.y if self.star else 0.0
        self.x = cx + self.orbit_radius * math.cos(self.angle)
        self.y = cy + self.orbit_radius * math.sin(self.angle)

    def step(self, dt: float) -> None:
        """Сдвинуть планету по своей круговой орбите на шаг dt.

        Угловая скорость уменьшается с ростом радиуса орбиты, что
        исключает столкновения планет одной звезды и не нарушает
        условие "орбиты планет всех звёзд пересекаются" (т.к. орбиты
        вокруг разных звёзд геометрически независимы).
        """
        sign = 1.0 if self.clockwise else -1.0
        omega = self.ANGULAR_SPEED / math.sqrt(self.orbit_index)
        self.angle += sign * omega * dt
        self._update_xy()
        for sat in self.satellites:
            sat.step(dt)


class Satellite(SpaceObject):
    """Спутник планеты, вращающийся вокруг неё по круговой орбите."""

    ORBIT_RADIUS = 14.0
    """Радиус орбиты спутника вокруг планеты."""
    ANGULAR_SPEED = 2.0
    """Угловая скорость спутника (рад/с) -- выше, чем у планеты,
    т.к. орбита спутника намного меньше."""

    def __init__(self, R: int, color: str, m: float,
                 angle0: float = 0.0, clockwise: bool = True) -> None:
        super().__init__(R, color, m)
        self.planet: Optional[Planet] = None
        self.angle: float = angle0
        self.clockwise: bool = clockwise
        self._update_xy()

    def _update_xy(self) -> None:
        """Пересчитать (x, y) спутника относительно его планеты."""
        px = self.planet.x if self.planet else 0.0
        py = self.planet.y if self.planet else 0.0
        self.x = px + self.ORBIT_RADIUS * math.cos(self.angle)
        self.y = py + self.ORBIT_RADIUS * math.sin(self.angle)

    def step(self, dt: float) -> None:
        """Сдвинуть спутник по орбите вокруг планеты на шаг dt.

        Радиус орбиты спутника фиксирован и меньше радиуса любой
        планетной орбиты, поэтому спутники не сталкиваются ни с
        планетами, ни между собой (у каждой планеты не более одного
        спутника в условиях Билета №7).
        """
        sign = 1.0 if self.clockwise else -1.0
        self.angle += sign * self.ANGULAR_SPEED * dt
        self._update_xy()


def build_ticket_7_system() -> List[SpaceObject]:
    """Строит систему согласно условиям Билета №7 и возвращает плоский
    список всех созданных объектов (звёзды, планеты, спутники) -- именно
    такой список ожидает главный модуль для отображения и обновления.
    """
    stars_spec = [
        # (R, color, m, x, y, planet_count, has_satellites_on_odd_orbits)
        (16, "yellow", 1.0e30, -260.0, 0.0, 10, False),
        (20, "orange", 1.6e30, 0.0, 0.0, 20, True),
        (16, "red", 1.0e30, 260.0, 0.0, 10, False),
    ]

    all_objects: List[SpaceObject] = []

    for (R, color, m, x, y, planet_count, with_sats) in stars_spec:
        star = Star(R, color, m, x, y)
        all_objects.append(star)

        def factory(orbit_index: int, angle0: float, clockwise: bool,
                    _with_sats=with_sats) -> Planet:
            planet = Planet(4, "green", 5.0e24,
                             orbit_index, angle0, clockwise)
            if _with_sats and orbit_index % 2 == 1:
                sat = Satellite(2, "white", 1.0e22, angle0=0.0,
                                 clockwise=True)
                planet.add_satellite(sat)
                all_objects.append(sat)
            return planet

        planets = star.populate_orbits(planet_count, factory)
        all_objects.extend(planets)

    return all_objects


if __name__ == "__main__":
    print("This module is not for direct call!")