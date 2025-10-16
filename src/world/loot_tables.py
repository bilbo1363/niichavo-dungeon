"""
Таблицы лута для процедурной генерации
"""
from enum import Enum
import random
from typing import List, Tuple, Optional


class LootPlacement(Enum):
    """Способы размещения лута"""
    FLOOR = "floor"  # На полу (видно сразу)
    CHEST = "chest"  # В сундуке (нужно открыть)
    HIDDEN = "hidden"  # В тайнике (нужно найти)
    TRAPPED = "trapped"  # За ловушкой (риск = награда)
    CORPSE = "corpse"  # У мёртвого искателя (скелет)


class LootRarity(Enum):
    """Редкость лута"""
    COMMON = "common"  # Обычный (70-50%)
    UNCOMMON = "uncommon"  # Необычный (25-35%)
    RARE = "rare"  # Редкий (5-15%)
    EPIC = "epic"  # Эпический (0-15%)
    LEGENDARY = "legendary"  # Легендарный (0-5%)


class LootSpot:
    """Место размещения лута"""
    
    def __init__(
        self,
        x: int,
        y: int,
        placement: LootPlacement,
        rarity: LootRarity,
        item_count: int = 1
    ):
        """
        Инициализация места лута
        
        Args:
            x: Позиция X
            y: Позиция Y
            placement: Способ размещения
            rarity: Редкость предметов
            item_count: Количество предметов
        """
        self.x = x
        self.y = y
        self.placement = placement
        self.rarity = rarity
        self.item_count = item_count


class LootTableGenerator:
    """Генератор таблиц лута"""
    
    @staticmethod
    def get_rarity_weights(floor: int) -> dict:
        """
        Получить веса редкости для этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Словарь с весами редкости
        """
        # Этажи 1-5: в основном обычные предметы
        if floor <= 5:
            return {
                LootRarity.COMMON: 70,
                LootRarity.UNCOMMON: 25,
                LootRarity.RARE: 5,
                LootRarity.EPIC: 0,
                LootRarity.LEGENDARY: 0
            }
        
        # Этажи 6-10: больше необычных
        elif floor <= 10:
            return {
                LootRarity.COMMON: 50,
                LootRarity.UNCOMMON: 35,
                LootRarity.RARE: 15,
                LootRarity.EPIC: 0,
                LootRarity.LEGENDARY: 0
            }
        
        # Этажи 11-15: редкие и эпические
        elif floor <= 15:
            return {
                LootRarity.COMMON: 30,
                LootRarity.UNCOMMON: 40,
                LootRarity.RARE: 20,
                LootRarity.EPIC: 10,
                LootRarity.LEGENDARY: 0
            }
        
        # Этажи 16-20: эпические и легендарные
        else:
            return {
                LootRarity.COMMON: 10,
                LootRarity.UNCOMMON: 30,
                LootRarity.RARE: 35,
                LootRarity.EPIC: 20,
                LootRarity.LEGENDARY: 5
            }
    
    @staticmethod
    def choose_rarity(floor: int) -> LootRarity:
        """
        Выбрать случайную редкость с учётом этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Редкость
        """
        weights = LootTableGenerator.get_rarity_weights(floor)
        rarities = list(weights.keys())
        weights_list = list(weights.values())
        
        return random.choices(rarities, weights=weights_list, k=1)[0]
    
    @staticmethod
    def get_loot_count_for_floor(floor: int) -> int:
        """
        Получить количество мест с лутом для этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Количество мест с лутом
        """
        # Базовое количество: 5-10 мест
        base_count = random.randint(5, 10)
        
        # Бонус от этажа (глубже = больше лута)
        floor_bonus = floor // 5
        
        return base_count + floor_bonus
    
    @staticmethod
    def generate_loot_spots(
        rooms: List,
        floor: int,
        special_rooms: List = None
    ) -> List[LootSpot]:
        """
        Сгенерировать места размещения лута
        
        Args:
            rooms: Список комнат
            floor: Номер этажа
            special_rooms: Список особых комнат
            
        Returns:
            Список мест с лутом
        """
        loot_spots = []
        
        if len(rooms) < 2:
            return loot_spots
        
        # Количество мест с лутом
        loot_count = LootTableGenerator.get_loot_count_for_floor(floor)
        
        # Пропускаем первую комнату (вход)
        available_rooms = rooms[1:]
        
        for _ in range(loot_count):
            if not available_rooms:
                break
            
            # Выбираем случайную комнату
            room = random.choice(available_rooms)
            
            # Случайная позиция в комнате
            margin = 1
            if room.width <= 2 * margin or room.height <= 2 * margin:
                continue
            
            x = room.x + margin + random.randint(0, room.width - 2 * margin - 1)
            y = room.y + margin + random.randint(0, room.height - 2 * margin - 1)
            
            # Выбираем способ размещения
            placement = LootTableGenerator._choose_placement(floor)
            
            # Выбираем редкость
            rarity = LootTableGenerator.choose_rarity(floor)
            
            # Количество предметов зависит от способа размещения
            if placement == LootPlacement.CHEST:
                item_count = random.randint(2, 4)
            elif placement == LootPlacement.HIDDEN:
                item_count = random.randint(1, 3)
            elif placement == LootPlacement.CORPSE:
                item_count = random.randint(1, 2)
            else:
                item_count = 1
            
            loot_spot = LootSpot(x, y, placement, rarity, item_count)
            loot_spots.append(loot_spot)
        
        # Добавляем особый лут для особых комнат
        if special_rooms:
            loot_spots.extend(
                LootTableGenerator._generate_special_room_loot(special_rooms, floor)
            )
        
        return loot_spots
    
    @staticmethod
    def _choose_placement(floor: int) -> LootPlacement:
        """
        Выбрать способ размещения лута
        
        Args:
            floor: Номер этажа
            
        Returns:
            Способ размещения
        """
        # Этажи 1-5: в основном на полу
        if floor <= 5:
            return random.choices(
                [LootPlacement.FLOOR, LootPlacement.CHEST, LootPlacement.CORPSE],
                weights=[60, 30, 10],
                k=1
            )[0]
        
        # Этажи 6-10: больше сундуков и трупов
        elif floor <= 10:
            return random.choices(
                [LootPlacement.FLOOR, LootPlacement.CHEST, LootPlacement.CORPSE, LootPlacement.HIDDEN],
                weights=[40, 35, 15, 10],
                k=1
            )[0]
        
        # Этажи 11-15: больше тайников
        elif floor <= 15:
            return random.choices(
                [LootPlacement.FLOOR, LootPlacement.CHEST, LootPlacement.HIDDEN, LootPlacement.TRAPPED, LootPlacement.CORPSE],
                weights=[25, 30, 25, 10, 10],
                k=1
            )[0]
        
        # Этажи 16-20: много ловушек и тайников
        else:
            return random.choices(
                [LootPlacement.CHEST, LootPlacement.HIDDEN, LootPlacement.TRAPPED, LootPlacement.CORPSE],
                weights=[30, 30, 25, 15],
                k=1
            )[0]
    
    @staticmethod
    def _generate_special_room_loot(special_rooms: List, floor: int) -> List[LootSpot]:
        """
        Сгенерировать лут для особых комнат
        
        Args:
            special_rooms: Список особых комнат
            floor: Номер этажа
            
        Returns:
            Список мест с лутом
        """
        from .special_rooms import SpecialRoomType
        
        loot_spots = []
        
        for special_room in special_rooms:
            # Сокровищница: много лута
            if special_room.room_type == SpecialRoomType.TREASURE:
                for _ in range(random.randint(10, 15)):
                    x = special_room.x + random.randint(2, special_room.width - 3)
                    y = special_room.y + random.randint(2, special_room.height - 3)
                    
                    # В сокровищнице лучший лут
                    rarity = random.choices(
                        [LootRarity.UNCOMMON, LootRarity.RARE, LootRarity.EPIC, LootRarity.LEGENDARY],
                        weights=[30, 40, 25, 5],
                        k=1
                    )[0]
                    
                    loot_spot = LootSpot(x, y, LootPlacement.CHEST, rarity, 1)
                    loot_spots.append(loot_spot)
            
            # Библиотека: записки и свитки (будет реализовано позже)
            elif special_room.room_type == SpecialRoomType.LIBRARY:
                for _ in range(random.randint(3, 6)):
                    x = special_room.x + random.randint(2, special_room.width - 3)
                    y = special_room.y + random.randint(2, special_room.height - 3)
                    
                    loot_spot = LootSpot(x, y, LootPlacement.FLOOR, LootRarity.COMMON, 1)
                    loot_spots.append(loot_spot)
            
            # Алтарь: особый предмет
            elif special_room.room_type == SpecialRoomType.ALTAR:
                cx, cy = special_room.center
                
                loot_spot = LootSpot(cx, cy, LootPlacement.FLOOR, LootRarity.EPIC, 1)
                loot_spots.append(loot_spot)
        
        return loot_spots
