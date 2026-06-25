# coding: utf-8
# license: GPLv3

from solar_objects import Star, Planet, Satellite

def read_space_objects_data_from_file(input_filename):
    """Считывает данные о космических объектах из файла и восстанавливает ООП-связи.
    Использует 3 прохода, чтобы сначала создать Звезды, потом Планеты, потом Спутники.
    """
    objects = []
    stars_by_id = {}
    planets_by_id = {}
    
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Файл {input_filename} не найден. Загружаем систему по умолчанию.")
        return []

    # Проход 1: Создаем Звезды
    for line in lines:
        parts = line.strip().split()
        if not parts or parts[0] == '#': continue
        
        if parts[0] == 'Star':
            # Формат: Star R color m x y star_id
            star = Star(int(parts[1]), parts[2], float(parts[3]), float(parts[4]), float(parts[5]))
            star_id = int(parts[6])
            stars_by_id[star_id] = star
            objects.append(star)
            
    # Проход 2: Создаем Планеты и привязываем их к Звездам
    for line in lines:
        parts = line.strip().split()
        if not parts or parts[0] == '#': continue
        
        if parts[0] == 'Planet':
            # Формат: Planet R color m orbit_index angle clockwise star_id
            orbit_index = int(parts[4])
            angle = float(parts[5])
            clockwise = bool(int(parts[6]))
            star_id = int(parts[7])
            saved_orbit_radius = float(parts[8])
            
            planet = Planet(int(parts[1]), parts[2], float(parts[3]), orbit_index, angle, clockwise)
            planet.orbit_radius = saved_orbit_radius
            planet._update_xy()  # Обновляем координаты планеты на основе сохранённого угла и радиуса орбиты
            # Восстанавливаем связь с родителем
            if star_id in stars_by_id:
                stars_by_id[star_id].add_planet(planet)
                
            planet_id = len(planets_by_id)
            planets_by_id[planet_id] = planet
            objects.append(planet)

    # Проход 3: Создаем Спутники и привязываем их к Планетам
    for line in lines:
        parts = line.strip().split()
        if not parts or parts[0] == '#': continue
        
        if parts[0] == 'Satellite':
            # Формат: Satellite R color m angle clockwise planet_id
            angle = float(parts[4])
            clockwise = bool(int(parts[5]))
            planet_id = int(parts[6])
            
            sat = Satellite(int(parts[1]), parts[2], float(parts[3]), angle, clockwise)
            
            # Восстанавливаем связь с родителем
            if planet_id in planets_by_id:
                planets_by_id[planet_id].add_satellite(sat)
                
            objects.append(sat)
            
    return objects

def write_space_objects_data_to_file(output_filename, space_objects):
    """Сохраняет кинематическое состояние и ООП-связи объектов в файл."""
    # Назначаем временные ID для восстановления связей при загрузке
    star_ids = {id(obj): i for i, obj in enumerate(space_objects) if isinstance(obj, Star)}
    planet_ids = {id(obj): i for i, obj in enumerate(space_objects) if isinstance(obj, Planet)}
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        for obj in space_objects:
            if isinstance(obj, Star):
                f.write(f"Star {obj.R} {obj.color} {obj.m} {obj.x} {obj.y} {star_ids[id(obj)]}\n")
            elif isinstance(obj, Planet):
                star_id = star_ids.get(id(obj.star), -1)
                # Сохраняем текущий угол (angle), чтобы при загрузке анимация продолжилась с того же места
                f.write(f"Planet {obj.R} {obj.color} {obj.m} {obj.orbit_index} {obj.angle} {int(obj.clockwise)} {star_id} {obj.orbit_radius}\n")
            elif isinstance(obj, Satellite):
                planet_id = planet_ids.get(id(obj.planet), -1)
                f.write(f"Satellite {obj.R} {obj.color} {obj.m} {obj.angle} {int(obj.clockwise)} {planet_id}\n")

if __name__ == "__main__":
    print("This module is not for direct call!")