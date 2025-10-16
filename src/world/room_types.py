"""
Типы комнат для процедурной генерации
"""
from enum import Enum
from typing import Tuple
import random


class RoomType(Enum):
    """Типы комнат"""
    NORMAL = "normal"  # Обычная комната
    CIRCULAR = "circular"  # Круглая комната
    L_SHAPED = "l_shaped"  # L-образная
    CROSS = "cross"  # Крестообразная
    HALL = "hall"  # Большой зал
    CORRIDOR = "corridor"  # Узкий коридор
    MAZE = "maze"  # Мини-лабиринт
    ARENA = "arena"  # Арена (круглая, без препятствий)
    TREASURE = "treasure"  # Сокровищница
    LIBRARY = "library"  # Библиотека


class RoomTemplate:
    """Шаблон комнаты"""
    
    def __init__(
        self,
        room_type: RoomType,
        min_width: int,
        max_width: int,
        min_height: int,
        max_height: int,
        weight: float = 1.0
    ):
        """
        Инициализация шаблона
        
        Args:
            room_type: Тип комнаты
            min_width: Минимальная ширина
            max_width: Максимальная ширина
            min_height: Минимальная высота
            max_height: Максимальная высота
            weight: Вес для случайного выбора (больше = чаще)
        """
        self.room_type = room_type
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height
        self.weight = weight
        
    def generate_size(self) -> Tuple[int, int]:
        """Сгенерировать случайный размер"""
        width = random.randint(self.min_width, self.max_width)
        height = random.randint(self.min_height, self.max_height)
        return (width, height)


# Шаблоны комнат
ROOM_TEMPLATES = {
    RoomType.NORMAL: RoomTemplate(
        RoomType.NORMAL,
        min_width=6, max_width=12,
        min_height=6, max_height=12,
        weight=5.0  # Самый частый тип
    ),
    RoomType.CIRCULAR: RoomTemplate(
        RoomType.CIRCULAR,
        min_width=8, max_width=14,
        min_height=8, max_height=14,
        weight=2.0
    ),
    RoomType.L_SHAPED: RoomTemplate(
        RoomType.L_SHAPED,
        min_width=10, max_width=16,
        min_height=10, max_height=16,
        weight=1.5
    ),
    RoomType.CROSS: RoomTemplate(
        RoomType.CROSS,
        min_width=12, max_width=18,
        min_height=12, max_height=18,
        weight=1.0
    ),
    RoomType.HALL: RoomTemplate(
        RoomType.HALL,
        min_width=20, max_width=30,
        min_height=15, max_height=25,
        weight=0.5  # Редкий
    ),
    RoomType.CORRIDOR: RoomTemplate(
        RoomType.CORRIDOR,
        min_width=3, max_width=5,
        min_height=10, max_height=20,
        weight=1.0
    ),
    RoomType.MAZE: RoomTemplate(
        RoomType.MAZE,
        min_width=15, max_width=20,
        min_height=15, max_height=20,
        weight=0.3  # Очень редкий
    ),
    RoomType.ARENA: RoomTemplate(
        RoomType.ARENA,
        min_width=12, max_width=18,
        min_height=12, max_height=18,
        weight=0.5
    ),
    RoomType.TREASURE: RoomTemplate(
        RoomType.TREASURE,
        min_width=6, max_width=10,
        min_height=6, max_height=10,
        weight=0.3  # Редкий
    ),
    RoomType.LIBRARY: RoomTemplate(
        RoomType.LIBRARY,
        min_width=10, max_width=15,
        min_height=8, max_height=12,
        weight=0.5
    ),
}


def get_random_room_type() -> RoomType:
    """
    Получить случайный тип комнаты с учётом весов
    
    Returns:
        Случайный тип комнаты
    """
    templates = list(ROOM_TEMPLATES.values())
    weights = [t.weight for t in templates]
    chosen_template = random.choices(templates, weights=weights, k=1)[0]
    return chosen_template.room_type


def get_room_template(room_type: RoomType) -> RoomTemplate:
    """
    Получить шаблон комнаты по типу
    
    Args:
        room_type: Тип комнаты
        
    Returns:
        Шаблон комнаты
    """
    return ROOM_TEMPLATES[room_type]
