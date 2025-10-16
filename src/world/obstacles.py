"""
Система препятствий и декораций
"""
from enum import Enum
import random
from typing import List, Tuple


class ObstacleType(Enum):
    """Типы препятствий"""
    PILLAR = "pillar"  # Колонна (блокирует движение, не видимость)
    TABLE = "table"  # Стол (можно обойти)
    STATUE = "statue"  # Статуя (декоративная)
    RUBBLE = "rubble"  # Обломки (случайные)
    PIT = "pit"  # Яма (нельзя пройти)
    WATER = "water"  # Вода (можно пройти, замедляет)
    LAVA = "lava"  # Лава (урон при прохождении)


class Obstacle:
    """Препятствие"""
    
    def __init__(
        self,
        x: int,
        y: int,
        obstacle_type: ObstacleType,
        blocks_movement: bool = True,
        blocks_vision: bool = False,
        damage: int = 0
    ):
        """
        Инициализация препятствия
        
        Args:
            x: Позиция X
            y: Позиция Y
            obstacle_type: Тип препятствия
            blocks_movement: Блокирует ли движение
            blocks_vision: Блокирует ли видимость
            damage: Урон при прохождении (если можно пройти)
        """
        self.x = x
        self.y = y
        self.obstacle_type = obstacle_type
        self.blocks_movement = blocks_movement
        self.blocks_vision = blocks_vision
        self.damage = damage


class ObstacleGenerator:
    """Генератор препятствий"""
    
    @staticmethod
    def generate_obstacles_for_room(
        room_x: int,
        room_y: int,
        room_width: int,
        room_height: int,
        floor: int
    ) -> List[Obstacle]:
        """
        Сгенерировать препятствия для комнаты
        
        Args:
            room_x: X координата комнаты
            room_y: Y координата комнаты
            room_width: Ширина комнаты
            room_height: Высота комнаты
            floor: Номер этажа
            
        Returns:
            Список препятствий
        """
        obstacles = []
        
        # Количество препятствий зависит от размера комнаты
        room_area = room_width * room_height
        num_obstacles = random.randint(
            max(1, room_area // 30),
            max(2, room_area // 20)
        )
        
        # Не размещаем препятствия слишком близко к краям
        margin = 2
        safe_width = room_width - 2 * margin
        safe_height = room_height - 2 * margin
        
        if safe_width < 2 or safe_height < 2:
            return obstacles  # Комната слишком маленькая
        
        for _ in range(num_obstacles):
            # Случайная позиция внутри комнаты (с отступом)
            x = room_x + margin + random.randint(0, safe_width - 1)
            y = room_y + margin + random.randint(0, safe_height - 1)
            
            # Выбираем тип препятствия в зависимости от этажа
            obstacle_type = ObstacleGenerator._choose_obstacle_type(floor)
            
            # Создаём препятствие с параметрами
            if obstacle_type == ObstacleType.PILLAR:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=True, blocks_vision=False)
            elif obstacle_type == ObstacleType.TABLE:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=True, blocks_vision=False)
            elif obstacle_type == ObstacleType.STATUE:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=True, blocks_vision=True)
            elif obstacle_type == ObstacleType.RUBBLE:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=True, blocks_vision=False)
            elif obstacle_type == ObstacleType.PIT:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=True, blocks_vision=False)
            elif obstacle_type == ObstacleType.WATER:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=False, blocks_vision=False, damage=0)
            elif obstacle_type == ObstacleType.LAVA:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=False, blocks_vision=False, damage=5)
            else:
                obstacle = Obstacle(x, y, obstacle_type, blocks_movement=True, blocks_vision=False)
            
            obstacles.append(obstacle)
        
        return obstacles
    
    @staticmethod
    def _choose_obstacle_type(floor: int) -> ObstacleType:
        """
        Выбрать тип препятствия в зависимости от этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Тип препятствия
        """
        # Этажи 1-5: Подземелье (столы, колонны, обломки)
        if floor <= 5:
            return random.choice([
                ObstacleType.PILLAR,
                ObstacleType.TABLE,
                ObstacleType.RUBBLE,
                ObstacleType.STATUE
            ])
        
        # Этажи 6-10: Катакомбы (статуи, обломки, ямы)
        elif floor <= 10:
            return random.choice([
                ObstacleType.STATUE,
                ObstacleType.RUBBLE,
                ObstacleType.PIT,
                ObstacleType.PILLAR
            ])
        
        # Этажи 11-15: Пещеры (вода, лава, обломки)
        elif floor <= 15:
            return random.choice([
                ObstacleType.WATER,
                ObstacleType.LAVA,
                ObstacleType.RUBBLE,
                ObstacleType.PIT
            ])
        
        # Этажи 16-20: Бездна (лава, ямы, статуи)
        else:
            return random.choice([
                ObstacleType.LAVA,
                ObstacleType.PIT,
                ObstacleType.STATUE,
                ObstacleType.RUBBLE
            ])
