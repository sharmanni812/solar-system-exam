# coding: utf-8
# license: GPLv3

from __future__ import annotations
import tkinter
from typing import List

from solar_vis import (
    window_width, window_height,
    calculate_scale_factor, create_object_image, create_orbit_image,
    update_object_position, update_system_name, set_orbits_visible,
)
from solar_objects import SpaceObject, Planet, Satellite, build_ticket_7_system
import solar_model #Импортируем модуль solar_model, чтобы использовать его функции и переменные
from solar_input import write_space_objects_data_to_file, read_space_objects_data_from_file

# --- Глобальные переменные ---
perform_execution = False
physical_time = 0.0
displayed_time = None
time_step = None
time_speed = None
orbits_visible = None
space_objects: List[SpaceObject] = []
space = None
start_button = None
physics_button = None # Кнопка физики
root_window = None  # Ссылка на главное окно Tkinter

# --- Новая функция ---
def toggle_physics():
    solar_model.PHYSICS_MODE = not solar_model.PHYSICS_MODE
    status = "PHYSICS ON" if solar_model.PHYSICS_MODE else "PHYSICS OFF"
    color = "#4CAF50" if solar_model.PHYSICS_MODE else "#f0f0f0"
    if physics_button:
        physics_button.config(text=status, bg=color)

#Парад планет
def align_in_ray():
    """Выстраивает все планеты и спутники в единый луч."""
    for obj in space_objects:
        if isinstance(obj, Planet) or isinstance(obj, Satellite):
            obj.angle = 0.0
            # Пересчитываем X, Y и начальные векторы скоростей Vx, Vy для новой позиции
            obj._update_xy() 
            update_object_position(space, obj)
    print("Планеты выстроены в луч!")

# --- Функции сохранения/загрузки ---
def save_to_file():
    """Сохраняет текущее состояние системы в файл."""
    write_space_objects_data_to_file("ticket7_save.txt", space_objects)
    print("Система сохранена в ticket7_save.txt")

def load_from_file():
    """Загружает состояние системы из файла и перерисовывает холст."""
    global space_objects
    space.delete("all")
    space_objects = read_space_objects_data_from_file("ticket7_save.txt")
    for obj in space_objects:
        if isinstance(obj, Planet):
            create_orbit_image(space, obj)
        create_object_image(space, obj)
    set_orbits_visible(space, orbits_visible.get())
    print("Система загружена из ticket7_save.txt")

# --- Функции управления симуляцией ---
def execution() -> None:
    global physical_time
    dt = time_step.get()

    # ИСПРАВЛЕНИЕ: Добавлено solar_model. перед вызовом функции
    solar_model.recalculate_space_objects_positions(space_objects, dt)
    
    for obj in space_objects:
        update_object_position(space, obj)
    physical_time += dt
    displayed_time.set("%.1f" % physical_time + " seconds gone")
    if perform_execution:
        space.after(101 - int(time_speed.get()), execution)

def start_execution() -> None:
    global perform_execution
    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution
    execution()
    print('Started execution...')

def stop_execution() -> None:
    global perform_execution
    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution
    print('Paused execution.')

def toggle_orbits() -> None:
    set_orbits_visible(space, orbits_visible.get())

def init_system() -> None:
    global space_objects
    space_objects = build_ticket_7_system()
    max_distance = max(max(abs(obj.x), abs(obj.y)) for obj in space_objects)
    calculate_scale_factor(max_distance if max_distance > 0 else 1.0)
    for obj in space_objects:
        if isinstance(obj, Planet):
            create_orbit_image(space, obj)
    for obj in space_objects:
        create_object_image(space, obj)
    update_system_name(space, "Тройная система (Билет №7)")

# --- НОВАЯ ЛОГИКА: Стартовый экран и переключение ---

def show_start_screen():
    """Отображает стартовый экран с кнопкой запуска симуляции."""
    global root_window
    root_window.configure(bg="black")
    
    # Фрейм для центрирования контента
    start_frame = tkinter.Frame(root_window, bg="black")
    start_frame.pack(expand=True)
    
    # Большой заголовок
    tkinter.Label(
        start_frame, text="СОЛНЕЧНАЯ СИСТЕМА", 
        font=("Arial", 42, "bold"), fg="white", bg="black"
    ).pack(pady=(0, 10))
    
    # Подзаголовок
    tkinter.Label(
        start_frame, text="Экзаменационный проект • Билет №7", 
        font=("Arial", 20), fg="#2196F3", bg="black"
    ).pack(pady=(0, 40))
    
    # Описание системы
    description = (
        "Тройная звёздная система\n\n"
        "• 3 звезды (10, 20 и 10 планет соответственно)\n"
        "• Пересекающиеся орбиты без столкновений\n"
        "• Планеты вращаются в разных направлениях\n"
        "• Спутники у планет второй звезды на нечётных орбитах"
    )
    tkinter.Label(
        start_frame, text=description, 
        font=("Arial", 14), fg="lightgray", bg="black", 
        justify="left"
    ).pack(pady=(0, 60))
    
    # Красивая кнопка запуска
    start_btn = tkinter.Button(
        start_frame, text="▶  НАЧАТЬ МОДЕЛИРОВАНИЕ",
        font=("Arial", 18, "bold"),
        bg="#2196F3", fg="white",
        activebackground="#1976D2", activeforeground="white",
        relief="flat", padx=40, pady=15, cursor="hand2",
        command=launch_simulation
    )
    start_btn.pack()

def launch_simulation():
    """Уничтожает стартовый экран и запускает симуляцию."""
    global root_window
    # Очищаем всё окно от стартового экрана
    for widget in root_window.winfo_children():
        widget.destroy()
        
    # Строим интерфейс симуляции
    build_simulation_ui()
    init_system()

def build_simulation_ui():
    """Создает холст и панель управления симуляцией."""
    global root_window, space, start_button, orbits_visible
    global physical_time, displayed_time, time_step, time_speed
    
    space = tkinter.Canvas(root_window, width=window_width, height=window_height, bg="black")
    space.pack(side=tkinter.TOP)

    frame = tkinter.Frame(root_window)
    frame.pack(side=tkinter.BOTTOM)

    start_button = tkinter.Button(frame, text="Start", command=start_execution, width=6)
    start_button.pack(side=tkinter.LEFT)

    #Кнопка переключения физики
    physics_button = tkinter.Button(frame, text="PHYSICS OFF", command=toggle_physics, width=12)
    physics_button.pack(side=tkinter.LEFT)

    #Кнопка выстраивания планет в луч
    ray_button = tkinter.Button(frame, text="Ray Mode", command=align_in_ray, width=10)
    ray_button.pack(side=tkinter.LEFT, padx=5)

    time_step = tkinter.DoubleVar()
    time_step.set(0.05)
    tkinter.Entry(frame, textvariable=time_step, width=6).pack(side=tkinter.LEFT)

    time_speed = tkinter.DoubleVar()
    time_speed.set(50)
    tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL, length=100).pack(side=tkinter.LEFT)

    orbits_visible = tkinter.BooleanVar()
    orbits_visible.set(False)
    tkinter.Checkbutton(
        frame, text="Show orbits", variable=orbits_visible, command=toggle_orbits
    ).pack(side=tkinter.LEFT)

    tkinter.Button(frame, text="Save", command=save_to_file, width=6).pack(side=tkinter.LEFT)
    tkinter.Button(frame, text="Load", command=load_from_file, width=6).pack(side=tkinter.LEFT)
    displayed_time = tkinter.StringVar()
    displayed_time.set(str(physical_time) + " seconds gone")
    tkinter.Label(frame, textvariable=displayed_time, width=30).pack(side=tkinter.RIGHT)

def main() -> None:
    """Главная функция: создает окно и показывает стартовый экран."""
    global physical_time, root_window
    print('Modelling started!')
    physical_time = 0.0

    root_window = tkinter.Tk()
    root_window.title("Solar system simulator — Билет №7")
    
    # Задаем размер окна, чтобы стартовый экран выглядел хорошо
    root_window.geometry(f"{window_width}x{window_height + 50}")

    # Показываем стартовый экран вместо симуляции
    show_start_screen()
    
    root_window.mainloop()
    print('Modelling finished!')

if __name__ == "__main__":
    main()