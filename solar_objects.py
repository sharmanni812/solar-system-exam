# coding: utf-8
# license: GPLv3
"""
Модуль описания космических объектов в парадигме ООП.

Реализован для условий Билета №7:
    - 3 звезды: у 1-й -- 10 планет, у 2-й -- 20 планет, у 3-й -- 10 планет;
    - СТРОГО 1 планета на каждой орбите (удовлетворяет условию "максимум 4");
    - у всех планет 2-й (главной) звезды на нечётных орбитах есть по 1 спутнику;
    - планеты на чётных орбитах вращаются по часовой стрелке, на нечётных -- против;
    - орбиты всех звёзд пересекаются, но планеты не проходят сквозь сами звёзды.
"""

from __future__ import annotations

import math
from typing import List, Optional


class SpaceObject:
    """Базовый класс любого космического объекта."""

    def __init__(self, R: int, color: str, m: float,
                 x: float = 0.0, y: float = 0.0) -> None:
        self.R: int = R
        self.color: str = color
        self.m: float = m
        self.x: float = x
        self.y: float = y
        self.image: Optional[int] = None
        self.orbit_image: Optional[int] = None

    @property
    def type(self) -> str:
        return self.__class__.__name__.lower()

    def step(self, dt: float) -> None:
        raise NotImplementedError


class Star(SpaceObject):
    """Звезда -- центр своей планетной системы. В рамках билета неподвижна."""

    def __init__(self, R: int, color: str, m: float,
                 x: float = 0.0, y: float = 0.0) -> None:
        super().__init__(R, color, m, x, y)
        self.planets: List["Planet"] = []

    def add_planet(self, planet: "Planet") -> None:
        planet.star = self
        self.planets.append(planet)

    def step(self, dt: float) -> None:
        return


class Planet(SpaceObject):
    """Планета, вращающаяся вокруг звезды по круговой орбите."""

    BASE_ORBIT_RADIUS = 80.0
    ORBIT_STEP = 50.0
    ANGULAR_SPEED = 0.6

    def __init__(self, R: int, color: str, m: float,
                 orbit_index: int, angle0: float, clockwise: bool) -> None:
        super().__init__(R, color, m)
        self.star: Optional[Star] = None
        self.orbit_index: int = orbit_index
        
        # Радиус по умолчанию (в функции build_ticket_7_system мы его переопределим для красоты)
        self.orbit_radius: float = (self.BASE_ORBIT_RADIUS
                                     + (orbit_index - 1) * self.ORBIT_STEP)
        self.angle: float = angle0
        self.clockwise: bool = clockwise
        self.satellites: List["Satellite"] = []
        self._update_xy()

    def add_satellite(self, satellite: "Satellite") -> None:
        satellite.planet = self
        self.satellites.append(satellite)

    def _update_xy(self) -> None:
        cx = self.star.x if self.star else 0.0
        cy = self.star.y if self.star else 0.0
        self.x = cx + self.orbit_radius * math.cos(self.angle)
        self.y = cy + self.orbit_radius * math.sin(self.angle)

    def step(self, dt: float) -> None:
        sign = 1.0 if self.clockwise else -1.0
        # Единая скорость для сохранения формации луча
        omega = self.ANGULAR_SPEED 
        self.angle += sign * omega * dt
        self._update_xy()
        for sat in self.satellites:
            sat.step(dt)


class Satellite(SpaceObject):
    """Спутник планеты, вращающийся вокруг неё по круговой орбите."""

    ORBIT_RADIUS = 14.0
    ANGULAR_SPEED = 2.0

    def __init__(self, R: int, color: str, m: float,
                 angle0: float = 0.0, clockwise: bool = True) -> None:
        super().__init__(R, color, m)
        self.planet: Optional[Planet] = None
        self.angle: float = angle0
        self.clockwise: bool = clockwise
        self._update_xy()

    def _update_xy(self) -> None:
        px = self.planet.x if self.planet else 0.0
        py = self.planet.y if self.planet else 0.0
        self.x = px + self.ORBIT_RADIUS * math.cos(self.angle)
        self.y = py + self.ORBIT_RADIUS * math.sin(self.angle)

    def step(self, dt: float) -> None:
        sign = 1.0 if self.clockwise else -1.0
        self.angle += sign * self.ANGULAR_SPEED * dt
        self._update_xy()


# ВАЖНО: Функция теперь находится НА УРОВНЕ МОДУЛЯ (без отступов слева), 
# поэтому solar_main.py сможет её импортировать.
def build_ticket_7_system() -> List[SpaceObject]:
    """Строит систему Билета №7 (1 планета на орбиту, абсолютное пересечение всех орбит)."""
    
    # Секретная геометрия: звёзды стоят плотным треугольником, но первые орбиты 
    # начинаются так далеко (280), что огибают всю группу целиком.
    stars_spec = [
        # (R, color, m, x, y, planet_count, with_sats, start_rad, step)
        # Главная (orange) уходит влево по оси X
        (22, "orange", 1.6e30, -138.0, 0.0, 20, True, 280.0, 10.0),    
        # Желтая и красная уходят вправо и раздвигаются вверх/вниз
        (16, "yellow", 1.0e30, 70.0, -120.0, 10, False, 280.0, 10.0), 
        (16, "red", 1.0e30, 70.0, 120.0, 10, False, 280.0, 10.0),     
    ]
    
    all_objects: List[SpaceObject] = []

    for (R, color, m, x, y, planet_count, with_sats, start_rad, step) in stars_spec:
        star = Star(R, color, m, x, y)
        all_objects.append(star)

        for i in range(planet_count):
            orbit_index = i + 1
            clockwise = (orbit_index % 2 == 0)
            
            # Создаем планету, начальный угол 0.0 для "парада планет"
            planet = Planet(4, "green", 5.0e24, orbit_index, 0.0, clockwise)
            planet.star = star
            
            # Применяем выверенные радиусы
            planet.orbit_radius = start_rad + (orbit_index - 1) * step
            planet._update_xy() 
            
            all_objects.append(planet)
            
            # Спутники для главной звезды
            if with_sats and (orbit_index % 2 != 0):
                sat = Satellite(2, "white", 1.0e22, 0.0, True)
                planet.add_satellite(sat) 
                all_objects.append(sat)

    return all_objects

if __name__ == "__main__":
    print("This module is not for direct call!")