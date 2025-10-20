"""
Генератор уровней с детерминированным seed
"""
import numpy as np
import hashlib
import random
from typing import List, Tuple, Optional
from .level import Level
from .floor_state import FloorStateManager
from .room_types import RoomType, get_random_room_type, get_room_template
from .obstacles import ObstacleGenerator, Obstacle
from .traps import TrapGenerator, Trap
from .special_rooms import SpecialRoomGenerator, SpecialRoomType, SpecialRoom
from .loot_tables import LootTableGenerator, LootSpot, LootPlacement, LootRarity
from .lore_system import LoreGenerator, Note
from .biomes import BiomeManager, BiomeDecorator
from .containers import Container, ContainerType


class Room:
    """Класс комнаты"""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int,
        room_type: RoomType = RoomType.NORMAL
    ):
        """
        Инициализация комнаты
        
        Args:
            x: Позиция X (левый верхний угол)
            y: Позиция Y (левый верхний угол)
            width: Ширина комнаты
            height: Высота комнаты
            room_type: Тип комнаты
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type
        self.obstacles: List[Obstacle] = []
        self.is_special = False
        
    @property
    def center(self) -> Tuple[int, int]:
        """Центр комнаты"""
        return (self.x + self.width // 2, self.y + self.height // 2)
        
    def intersects(self, other: 'Room') -> bool:
        """
        Проверка пересечения с другой комнатой
        
        Args:
            other: Другая комната
            
        Returns:
            True если комнаты пересекаются
        """
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)


class LevelGenerator:
    """Генератор уровней"""
    
    def __init__(self, game_id: str = "default"):
        """
        Инициализация генератора
        
        Args:
            game_id: Уникальный ID игры для генерации seed
        """
        self.game_id = game_id
        self.floor_state_manager = FloorStateManager()
        
        print(f"🎲 Генератор создан (game_id: {game_id})")
        
    def generate_seed(self, floor: int) -> int:
        """
        Генерация детерминированного seed для этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Seed для генерации
        """
        # Создаём уникальный seed на основе game_id и номера этажа
        data = f"{self.game_id}_{floor}".encode()
        hash_obj = hashlib.sha256(data)
        seed = int.from_bytes(hash_obj.digest()[:4], 'big')
        return seed
        
    def generate(self, floor: int, width: int = 60, height: int = 40) -> Level:
        """
        Генерация уровня
        
        Args:
            floor: Номер этажа
            width: Ширина уровня
            height: Высота уровня
            
        Returns:
            Сгенерированный уровень
        """
        # Генерируем seed
        seed = self.generate_seed(floor)
        
        # Получаем или создаём состояние этажа
        floor_state = self.floor_state_manager.get_or_create_floor_state(floor, seed)
        
        # Проверяем, стабилизирован ли этаж
        if floor_state.is_stabilized:
            print(f"\n🔒 Загрузка стабилизированного этажа {floor}")
            return self._load_stabilized_floor(floor_state, width, height)
        
        # Если не стабилизирован - генерируем СЛУЧАЙНО (без seed!)
        # Используем текущее время для случайности
        import time
        random_seed = int(time.time() * 1000) % 2**32
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        # Получаем биом для этажа
        biome = BiomeManager.get_biome_for_floor(floor)
        
        print(f"\n🏗️  Генерация этажа {floor} (случайная планировка, seed: {random_seed})")
        print(f"   🎨 Биом: {biome.name} - {biome.description}")
        print(f"   ⚠️  Этаж НЕ стабилизирован - планировка изменится при возврате!")
        
        # Создаём пустой уровень с номером этажа (для биома)
        level = Level(width, height, floor_number=floor)
        level.tiles.fill(Level.TILE_WALL)  # Заполняем стенами
        
        # Генерируем комнаты (BSP алгоритм)
        rooms = self._generate_rooms_bsp(width, height, floor)
        
        # Вырезаем комнаты в уровне
        for room in rooms:
            self._carve_room(level, room)
            
        # Соединяем комнаты коридорами
        self._connect_rooms(level, rooms)
        
        # Генерируем препятствия для каждой комнаты
        self._generate_obstacles(rooms, floor)
        
        # Собираем все препятствия и добавляем в уровень
        all_obstacles = []
        for room in rooms:
            all_obstacles.extend(room.obstacles)
        level.obstacles = all_obstacles
        
        # Генерируем ловушки для этажа
        traps = TrapGenerator.generate_traps_for_floor(rooms, floor)
        level.traps = traps
        print(f"   🪤 Сгенерировано ловушек: {len(traps)}")
        
        # Определяем особые комнаты
        special_rooms = self._generate_special_rooms(rooms, floor)
        if special_rooms:
            print(f"   ✨ Особых комнат: {len(special_rooms)}")
            for sr in special_rooms:
                print(f"      - {sr.get_description()}")
        
        # Генерируем места для лута (улучшенная система)
        loot_spots = LootTableGenerator.generate_loot_spots(rooms, floor, special_rooms)
        print(f"   🎁 Мест с лутом: {len(loot_spots)}")
        
        # Генерируем записки и лор
        notes = LoreGenerator.generate_notes_for_floor(rooms, floor, special_rooms)
        level.notes = notes
        print(f"   📜 Записок: {len(notes)}")
        
        # Генерируем интерактивные объекты (доски и кости)
        from .interactive_objects import InteractiveObjectManager
        walkable_tiles = []
        for room in rooms:
            for x in range(room.x + 1, room.x + room.width - 1):
                for y in range(room.y + 1, room.y + room.height - 1):
                    if level.tiles[y, x] == Level.TILE_FLOOR:
                        walkable_tiles.append((x, y))
        
        interactive_objects = InteractiveObjectManager.generate_objects_for_floor(
            floor, width, height, walkable_tiles
        )
        level.interactive_objects = interactive_objects
        print(f"   📋 Интерактивных объектов: {len(interactive_objects)}")
        
        # Добавляем декорации биома
        BiomeDecorator.add_biome_decorations(level, rooms, floor)
        print(f"   🎨 Декорации биома добавлены")
        
        # Добавляем вход и выход
        if len(rooms) > 0:
            # Вход в первой комнате
            entrance_room = rooms[0]
            level.entrance_pos = entrance_room.center
            
            # Выход в последней комнате
            exit_room = rooms[-1]
            level.exit_pos = exit_room.center
            
            # Спавним руну устойчивости в случайной комнате (не первая и не последняя)
            if len(rooms) > 2:
                rune_room_idx = random.randint(1, len(rooms) - 2)
                rune_room = rooms[rune_room_idx]
                rune_x, rune_y = rune_room.center
                level.rune_manager.spawn_stability_rune(rune_x, rune_y)
                
            # Генерируем места для лута (LootSpots)
            loot_spots = LootTableGenerator.generate_loot_spots(rooms, floor, special_rooms)
            print(f"   💎 Мест для лута: {len(loot_spots)}")
            
            # Создаём контейнеры и предметы на основе LootSpots
            self._generate_loot_from_spots(level, loot_spots, floor)
            
            # Спавним врагов
            level.enemy_spawner.spawn_enemies(level, floor)
            
            # Спавним загадку ОДИН РАЗ при первой генерации
            if not floor_state.riddle_spawned and len(rooms) > 0:
                # Выбираем случайную комнату (не первая и не последняя)
                if len(rooms) > 2:
                    riddle_room_idx = random.randint(1, len(rooms) - 2)
                    riddle_room = rooms[riddle_room_idx]
                    riddle_x, riddle_y = riddle_room.center
                    level.riddle_manager.spawn_riddle(riddle_x, riddle_y, floor)
                    floor_state.riddle_spawned = True
                    floor_state.riddle_positions.append((riddle_x, riddle_y))
                    print(f"   ❓ Загадка заспавнена при генерации этажа на ({riddle_x}, {riddle_y})")
            
        print(f"✅ Этаж {floor} сгенерирован: {len(rooms)} комнат")
        
        return level
        
    def _load_stabilized_floor(
        self, 
        floor_state, 
        width: int, 
        height: int
    ) -> Level:
        """
        Загрузить стабилизированный этаж
        
        Args:
            floor_state: Состояние этажа
            width: Ширина уровня
            height: Высота уровня
            
        Returns:
            Загруженный уровень
        """
        saved_data = floor_state.get_saved_data()
        
        if saved_data is None:
            print("⚠️  Ошибка загрузки стабилизированного этажа")
            # Генерируем заново как fallback
            return self.generate(floor_state.floor_number, width, height)
            
        # Создаём уровень с номером этажа (для биома)
        level = Level(width, height, floor_number=floor_state.floor_number)
        level.tiles = saved_data['tiles'].copy()
        level.entrance_pos = saved_data['entrance_pos']
        level.exit_pos = saved_data['exit_pos']
        
        # Восстанавливаем fog of war
        if saved_data['fog_of_war'] is not None:
            level.fog_of_war.visibility = saved_data['fog_of_war'].copy()
            print(f"   🌫️  Разведанные области восстановлены")
        
        # Восстанавливаем загадки из сохранённых позиций
        if 'riddle_positions' in saved_data and saved_data['riddle_positions']:
            for riddle_x, riddle_y in saved_data['riddle_positions']:
                level.riddle_manager.spawn_riddle(riddle_x, riddle_y, floor_state.floor_number)
            print(f"   ❓ Восстановлено загадок: {len(saved_data['riddle_positions'])}")
        
        print(f"✅ Стабилизированный этаж {floor_state.floor_number} загружен")
        
        return level
        
    def _generate_rooms_bsp(
        self, 
        width: int, 
        height: int, 
        floor: int
    ) -> List[Room]:
        """
        Генерация комнат с помощью BSP (Binary Space Partitioning)
        
        Args:
            width: Ширина уровня
            height: Высота уровня
            floor: Номер этажа (влияет на количество комнат)
            
        Returns:
            Список комнат
        """
        rooms = []
        
        # Количество комнат зависит от этажа
        num_rooms = min(5 + floor // 2, 15)  # От 5 до 15 комнат
        
        # Пытаемся создать комнаты
        for _ in range(num_rooms * 3):  # Больше попыток для надежности
            # Случайный размер комнаты
            room_width = random.randint(5, 12)
            room_height = random.randint(5, 10)
            
            # Случайная позиция
            x = random.randint(1, width - room_width - 1)
            y = random.randint(1, height - room_height - 1)
            
            # Создаём комнату
            new_room = Room(x, y, room_width, room_height)
            
            # Проверяем пересечения
            if not any(new_room.intersects(other) for other in rooms):
                rooms.append(new_room)
                
            # Если достигли нужного количества - выходим
            if len(rooms) >= num_rooms:
                break
                
        return rooms
        
    def _carve_room(self, level: Level, room: Room) -> None:
        """
        Вырезать комнату в уровне
        
        Args:
            level: Уровень
            room: Комната
        """
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < level.width and 0 <= y < level.height:
                    level.tiles[y, x] = Level.TILE_FLOOR
                    
    def _connect_rooms(self, level: Level, rooms: List[Room]) -> None:
        """
        Соединить комнаты коридорами
        
        Args:
            level: Уровень
            rooms: Список комнат
        """
        # Соединяем каждую комнату со следующей
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]
            
            # Получаем центры комнат
            x1, y1 = room1.center
            x2, y2 = room2.center
            
            # Случайно выбираем: сначала горизонталь или вертикаль
            if random.random() < 0.5:
                # Горизонталь, потом вертикаль
                self._carve_h_corridor(level, x1, x2, y1)
                self._carve_v_corridor(level, y1, y2, x2)
            else:
                # Вертикаль, потом горизонталь
                self._carve_v_corridor(level, y1, y2, x1)
                self._carve_h_corridor(level, x1, x2, y2)
                
    def _carve_h_corridor(self, level: Level, x1: int, x2: int, y: int) -> None:
        """
        Вырезать горизонтальный коридор
        
        Args:
            level: Уровень
            x1: Начальная X
            x2: Конечная X
            y: Y координата
        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < level.width and 0 <= y < level.height:
                level.tiles[y, x] = Level.TILE_FLOOR
                
    def _carve_v_corridor(self, level: Level, y1: int, y2: int, x: int) -> None:
        """
        Вырезать вертикальный коридор
        
        Args:
            level: Уровень
            y1: Начальная Y
            y2: Конечная Y
            x: X координата
        """
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < level.width and 0 <= y < level.height:
                level.tiles[y, x] = Level.TILE_FLOOR
    
    def _generate_obstacles(self, rooms: List[Room], floor: int) -> None:
        """
        Генерация препятствий для комнат
        
        Args:
            rooms: Список комнат
            floor: Номер этажа
        """
        total_obstacles = 0
        
        for room in rooms:
            # Не генерируем препятствия в первой комнате (вход)
            if room == rooms[0]:
                continue
            
            # Генерируем препятствия
            obstacles = ObstacleGenerator.generate_obstacles_for_room(
                room.x, room.y, room.width, room.height, floor
            )
            room.obstacles = obstacles
            total_obstacles += len(obstacles)
        
        print(f"   🗿 Сгенерировано препятствий: {total_obstacles}")
    
    def _generate_special_rooms(
        self, 
        rooms: List[Room], 
        floor: int
    ) -> List[SpecialRoom]:
        """
        Определение особых комнат
        
        Args:
            rooms: Список комнат
            floor: Номер этажа
            
        Returns:
            Список особых комнат
        """
        special_rooms = []
        
        # Пропускаем первую и последнюю комнату
        if len(rooms) < 3:
            return special_rooms
        
        available_rooms = rooms[1:-1]
        
        # Проверяем каждый тип особой комнаты
        for room_type in SpecialRoomType:
            if SpecialRoomGenerator.should_generate_special_room(floor, room_type):
                # Выбираем случайную доступную комнату
                if not available_rooms:
                    break
                
                room = random.choice(available_rooms)
                special_room = SpecialRoomGenerator.create_special_room(room_type, room)
                
                if special_room:
                    special_rooms.append(special_room)
                    room.is_special = True
                    available_rooms.remove(room)  # Убираем из доступных
        
        return special_rooms
    
    def _generate_loot_from_spots(self, level: Level, loot_spots: List[LootSpot], floor: int) -> None:
        """
        Генерация контейнеров и предметов на основе LootSpots
        
        Args:
            level: Уровень
            loot_spots: Список мест для лута
            floor: Номер этажа
        """
        for loot_spot in loot_spots:
            # Определяем тип контейнера на основе способа размещения
            if loot_spot.placement == LootPlacement.CHEST:
                # Золотой сундук для редкого лута
                if loot_spot.rarity in [LootRarity.EPIC, LootRarity.LEGENDARY]:
                    container_type = ContainerType.GOLDEN_CHEST
                else:
                    container_type = ContainerType.CHEST
                    
            elif loot_spot.placement == LootPlacement.HIDDEN:
                container_type = ContainerType.HIDDEN_STASH
                
            elif loot_spot.placement == LootPlacement.CORPSE:
                container_type = ContainerType.CORPSE
                
            elif loot_spot.placement == LootPlacement.TRAPPED:
                # За ловушкой - обычно сундук
                container_type = ContainerType.CHEST
                
            else:  # FLOOR
                # На полу - просто спавним предметы без контейнера
                for _ in range(loot_spot.item_count):
                    level.item_spawner.spawn_random_items(level, floor, 1)
                continue
            
            # Генерируем предметы для контейнера
            items = []
            for _ in range(loot_spot.item_count):
                # Получаем случайный предмет с учётом редкости
                item = self._get_random_item_by_rarity(loot_spot.rarity, floor)
                if item:
                    items.append(item)
            
            # Создаём контейнер
            container = Container(loot_spot.x, loot_spot.y, container_type, items)
            level.containers.append(container)
        
        print(f"   📦 Контейнеров: {len(level.containers)}")
    
    def _get_random_item_by_rarity(self, rarity: 'LootRarity', floor: int):
        """
        Получить случайный предмет с учётом редкости
        
        Args:
            rarity: Желаемая редкость
            floor: Номер этажа
            
        Returns:
            Предмет или None
        """
        from ..items.item import ItemDatabase, ItemRarity
        
        # Маппинг редкости лута на редкость предметов
        rarity_map = {
            LootRarity.COMMON: ItemRarity.COMMON,
            LootRarity.UNCOMMON: ItemRarity.UNCOMMON,
            LootRarity.RARE: ItemRarity.RARE,
            LootRarity.EPIC: ItemRarity.EPIC,
            LootRarity.LEGENDARY: ItemRarity.LEGENDARY,
        }
        
        item_rarity = rarity_map.get(rarity, ItemRarity.COMMON)
        
        # Получаем базу данных предметов
        item_db = ItemDatabase()
        
        # Фильтруем предметы по редкости
        matching_items = [
            item_id for item_id, item in item_db.items.items()
            if item.rarity == item_rarity
        ]
        
        # Если нет предметов нужной редкости, берём любой
        if not matching_items:
            matching_items = list(item_db.items.keys())
        
        # Выбираем случайный предмет
        if matching_items:
            item_id = random.choice(matching_items)
            return item_db.get_item(item_id)
        
        return None


if __name__ == "__main__":
    # Тест генератора
    generator = LevelGenerator("test_game")
    
    # Генерируем несколько этажей
    for floor in [1, 5, 10]:
        level = generator.generate(floor)
        print(f"Этаж {floor}: {level.width}x{level.height}")
        
    # Проверяем детерминированность
    print("\nПроверка детерминированности:")
    seed1 = generator.generate_seed(1)
    seed2 = generator.generate_seed(1)
    print(f"Seed для этажа 1 (первый раз): {seed1}")
    print(f"Seed для этажа 1 (второй раз): {seed2}")
    print(f"Одинаковые: {seed1 == seed2}")
