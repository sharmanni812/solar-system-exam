# coding: utf-8
# license: GPLv3

"""
Главный модуль программы.
Собирает систему согласно Билету №7 (через `solar_objects.build_ticket_7_system`),
создаёт окно tkinter и запускает цикл моделирования.
Интерфейс позволяет:
- запускать/приостанавливать ход времени (кнопка Start/Pause);
- регулировать скорость моделирования (слайдер);
- включать/выключать отображение орбит (чекбокс "Show orbits");
- сохранять и загружать состояние системы из файла.
"""

from __future__ import annotations
import tkinter
from typing import List

from solar_vis import (
    window_width, window_height,
    calculate_scale_factor, create_object_image, create_orbit_image,
    update_object_position, update_system_name, set_orbits_visible,
)
from solar_objects import SpaceObject, Planet, build_ticket_7_system
from solar_model import recalculate_space_objects_positions
from solar_input import write_space_objects_data_to_file, read_space_objects_data_from_file

perform_execution = False
"""Флаг цикличности выполнения расчёта."""
physical_time = 0.0
"""Физическое время от начала расчёта."""
displayed_time = None
"""Отображаемое на экране время (переменная tkinter)."""
time_step = None
"""Шаг по времени при моделировании (переменная tkinter)."""
time_speed = None
"""Скорость воспроизведения, управляется слайдером (переменная tkinter)."""
orbits_visible = None
"""Флаг отображения орбит (переменная tkinter, BooleanVar)."""
space_objects: List[SpaceObject] = []
"""Список всех космических объектов (звёзды, планеты, спутники)."""
space = None
start_button = None

def save_to_file():
    """Сохраняет текущее состояние системы в файл."""
    write_space_objects_data_to_file("ticket7_save.txt", space_objects)
    print("Система сохранена в ticket7_save.txt")

def load_from_file():
    """Загружает состояние системы из файла и перерисовывает холст."""
    global space_objects
    space.delete("all")  # Очищаем холст
    space_objects = read_space_objects_data_from_file("ticket7_save.txt")
    
    # Заново создаем образы и орбиты
    for obj in space_objects:
        if isinstance(obj, Planet):
            create_orbit_image(space, obj)
        create_object_image(space, obj)
        
    set_orbits_visible(space, orbits_visible.get())
    print("Система загружена из ticket7_save.txt")

def execution() -> None:
    """Функция исполнения -- выполняется циклически: продвигает все
    объекты на шаг времени и обновляет их положение на холсте.
    """
    global physical_time
    dt = time_step.get()
    
    # Используем физическую модель, которая внутри вызывает кинематику step()
    recalculate_space_objects_positions(space_objects, dt)
    
    for obj in space_objects:
        update_object_position(space, obj)
        
    physical_time += dt
    displayed_time.set("%.1f" % physical_time + " seconds gone")
    
    if perform_execution:
        space.after(101 - int(time_speed.get()), execution)

def start_execution() -> None:
    """Обработчик нажатия на кнопку Start. Запускает цикл execution()."""
    global perform_execution
    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution
    execution()
    print('Started execution...')

def stop_execution() -> None:
    """Обработчик нажатия на кнопку Pause. Останавливает цикл execution()."""
    global perform_execution
    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution
    print('Paused execution.')

def toggle_orbits() -> None:
    """Обработчик чекбокса "Show orbits": показывает/скрывает все орбиты."""
    set_orbits_visible(space, orbits_visible.get())

def init_system() -> None:
    """Строит систему по условиям Билета №7, вычисляет масштаб и создаёт
    графические образы всех объектов и орбит планет.
    """
    global space_objects
    space_objects = build_ticket_7_system()
    
    max_distance = max(
        max(abs(obj.x), abs(obj.y)) for obj in space_objects
    )
    calculate_scale_factor(max_distance if max_distance > 0 else 1.0)

    for obj in space_objects:
        if isinstance(obj, Planet):
            create_orbit_image(space, obj)

    for obj in space_objects:
        create_object_image(space, obj)

    update_system_name(space, "Тройная система (Билет №7)")

def main() -> None:
    """Главная функция: создаёт окно, холст, панель управления и
    инициализирует систему небесных тел.
    """
    global physical_time, displayed_time, time_step, time_speed
    global space, start_button, orbits_visible
    
    print('Modelling started!')
    physical_time = 0.0

    root = tkinter.Tk()
    root.title("Solar system simulator — Билет №7")

    space = tkinter.Canvas(root, width=window_width, height=window_height,
                           bg="black")
    space.pack(side=tkinter.TOP)

    frame = tkinter.Frame(root)
    frame.pack(side=tkinter.BOTTOM)

    start_button = tkinter.Button(frame, text="Start",
                                  command=start_execution, width=6)
    start_button.pack(side=tkinter.LEFT)

    time_step = tkinter.DoubleVar()
    time_step.set(0.05)
    time_step_entry = tkinter.Entry(frame, textvariable=time_step, width=6)
    time_step_entry.pack(side=tkinter.LEFT)

    time_speed = tkinter.DoubleVar()
    time_speed.set(50)
    scale = tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL, length=100)
    scale.pack(side=tkinter.LEFT)

    orbits_visible = tkinter.BooleanVar()
    orbits_visible.set(False)
    orbits_checkbox = tkinter.Checkbutton(
        frame, text="Show orbits", variable=orbits_visible,
        command=toggle_orbits)
    orbits_checkbox.pack(side=tkinter.LEFT)

    # Кнопки сохранения и загрузки (корректно привязаны к frame)
    save_btn = tkinter.Button(frame, text="Save", command=save_to_file, width=6)
    save_btn.pack(side=tkinter.LEFT)
    
    load_btn = tkinter.Button(frame, text="Load", command=load_from_file, width=6)
    load_btn.pack(side=tkinter.LEFT)

    displayed_time = tkinter.StringVar()
    displayed_time.set(str(physical_time) + " seconds gone")
    time_label = tkinter.Label(frame, textvariable=displayed_time, width=30)
    time_label.pack(side=tkinter.RIGHT)

    init_system()

    root.mainloop()
    print('Modelling finished!')

if __name__ == "__main__":
    main()