# coding: utf-8
# license: GPLv3

gravitational_constant = 6.67408E-11
"""Гравитационная постоянная Ньютона G"""


def calculate_force(body, space_objects):
    """Вычисляет силу, действующую на тело.

    Для каждого другого объекта system'ы вычисляется гравитационная сила
    по закону Ньютона:
        F = G * m1 * m2 / r^2
    и раскладывается на компоненты Fx, Fy пропорционально (dx/r, dy/r).

    Параметры:

    **body** — тело, для которого нужно вычислить дейстующую силу.
    **space_objects** — список объектов, которые воздействуют на тело.
    """

    body.Fx = body.Fy = 0
    for obj in space_objects:
        if body == obj:
            continue  # тело не действует гравитационной силой на само себя!
        r = ((body.x - obj.x) ** 2 + (body.y - obj.y) ** 2) ** 0.5
        if r == 0:
            continue  # избегаем деления на ноль при совпадении координат
        force = gravitational_constant * body.m * obj.m / r ** 2
        # компоненты силы направлены от body к obj (притяжение)
        body.Fx += force * (obj.x - body.x) / r
        body.Fy += force * (obj.y - body.y) / r


def move_space_object(body, dt):
    """Перемещает тело в соответствии с действующей на него силой.

    Используется метод Эйлера: сначала обновляется скорость по
    ускорению a = F/m, затем по новой скорости обновляется координата.

    Параметры:

    **body** — тело, которое нужно переместить.
    **dt** — шаг по времени.

    Вместо того, чтобы использовать метод Эйлера, можно использовать 
    кинематическую модель step() для сохранения стабильности пересекающихся орбит. 
    """
    """ax = body.Fx / body.m
    ay = body.Fy / body.m
    body.Vx += ax * dt
    body.Vy += ay * dt
    body.x += body.Vx * dt
    body.y += body.Vy * dt"""
    if hasattr(body, 'step'):
        body.step(dt)  # для планет и спутников вызываем их метод step()


def recalculate_space_objects_positions(space_objects, dt):
    """Пересчитывает координаты объектов.

    Параметры:

    **space_objects** — список оьъектов, для которых нужно пересчитать координаты.
    **dt** — шаг по времени
    """

    for body in space_objects:
        calculate_force(body, space_objects)
    for body in space_objects:
        move_space_object(body, dt)


if __name__ == "__main__":
    print("This module is not for direct call!")
