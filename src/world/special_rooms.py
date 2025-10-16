"""
Особые комнаты (сокровищницы, библиотеки, алтари и т.д.)
"""
from enum import Enum
from typing import Optional


class SpecialRoomType(Enum):
    """Типы особых комнат"""
    TREASURE = "treasure"  # Сокровищница
    LIBRARY = "library"  # Библиотека
    ALTAR = "altar"  # Алтарь
    ARENA = "arena"  # Арена
    FOUNTAIN = "fountain"  # Фонтан
    SHOP = "shop"  # Магазин


class SpecialRoom:
    """Особая комната"""
    
    def __init__(
        self,
        room_type: SpecialRoomType,
        x: int,
        y: int,
        width: int,
        height: int
    ):
        """
        Инициализация особой комнаты
        
        Args:
            room_type: Тип комнаты
            x: Позиция X
            y: Позиция Y
            width: Ширина
            height: Высота
        """
        self.room_type = room_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.used = False  # Была ли использована (для фонтанов и т.д.)
        
    @property
    def center(self):
        """Центр комнаты"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def get_description(self) -> str:
        """Получить описание комнаты"""
        descriptions = {
            SpecialRoomType.TREASURE: "Сокровищница! Множество предметов, но охраняется врагами.",
            SpecialRoomType.LIBRARY: "Библиотека. Здесь можно найти знания и записки.",
            SpecialRoomType.ALTAR: "Древний алтарь. Можно принести жертву за благословение.",
            SpecialRoomType.ARENA: "Арена! Волны врагов ждут храбрецов.",
            SpecialRoomType.FOUNTAIN: "Фонтан. Его воды могут исцелить... или навредить.",
            SpecialRoomType.SHOP: "Магазин странствующего торговца.",
        }
        return descriptions.get(self.room_type, "Особая комната")


class SpecialRoomGenerator:
    """Генератор особых комнат"""
    
    @staticmethod
    def should_generate_special_room(floor: int, room_type: SpecialRoomType) -> bool:
        """
        Проверить, нужно ли генерировать особую комнату на этом этаже
        
        Args:
            floor: Номер этажа
            room_type: Тип комнаты
            
        Returns:
            True если нужно генерировать
        """
        import random
        
        if room_type == SpecialRoomType.SHOP:
            # Магазин каждый 5-й этаж
            return floor % 5 == 0
        
        elif room_type == SpecialRoomType.TREASURE:
            # Сокровищница 1 на 5 этажей (20% шанс)
            return random.random() < 0.2
        
        elif room_type == SpecialRoomType.LIBRARY:
            # Библиотека на этажах 3, 7, 12, 17 (примерно)
            return floor in [3, 7, 12, 17] or random.random() < 0.1
        
        elif room_type == SpecialRoomType.ALTAR:
            # Алтарь редко (10% шанс)
            return random.random() < 0.1
        
        elif room_type == SpecialRoomType.ARENA:
            # Арена очень редко (5% шанс)
            return random.random() < 0.05
        
        elif room_type == SpecialRoomType.FOUNTAIN:
            # Фонтан иногда (15% шанс)
            return random.random() < 0.15
        
        return False
    
    @staticmethod
    def create_special_room(
        room_type: SpecialRoomType,
        room
    ) -> Optional[SpecialRoom]:
        """
        Создать особую комнату из обычной
        
        Args:
            room_type: Тип особой комнаты
            room: Обычная комната
            
        Returns:
            Особая комната или None
        """
        # Проверяем минимальный размер
        min_sizes = {
            SpecialRoomType.TREASURE: (6, 6),
            SpecialRoomType.LIBRARY: (8, 8),
            SpecialRoomType.ALTAR: (6, 6),
            SpecialRoomType.ARENA: (12, 12),
            SpecialRoomType.FOUNTAIN: (5, 5),
            SpecialRoomType.SHOP: (8, 8),
        }
        
        min_width, min_height = min_sizes.get(room_type, (5, 5))
        
        if room.width < min_width or room.height < min_height:
            return None
        
        return SpecialRoom(
            room_type,
            room.x,
            room.y,
            room.width,
            room.height
        )
    
    @staticmethod
    def get_item_count_for_special_room(room_type: SpecialRoomType, floor: int) -> int:
        """
        Получить количество предметов для особой комнаты
        
        Args:
            room_type: Тип комнаты
            floor: Номер этажа
            
        Returns:
            Количество предметов
        """
        import random
        
        if room_type == SpecialRoomType.TREASURE:
            # Сокровищница: много предметов
            return random.randint(10, 15)
        
        elif room_type == SpecialRoomType.LIBRARY:
            # Библиотека: записки и книги
            return random.randint(3, 6)
        
        elif room_type == SpecialRoomType.SHOP:
            # Магазин: товары
            return random.randint(8, 12)
        
        elif room_type == SpecialRoomType.ALTAR:
            # Алтарь: 1-2 особых предмета
            return random.randint(1, 2)
        
        return 0
