"""
Система биомов для визуального разнообразия этажей
"""
from enum import Enum
from typing import Tuple


class BiomeType(Enum):
    """Типы биомов"""
    DUNGEON = "dungeon"  # Подземелье (этажи 1-5)
    CATACOMBS = "catacombs"  # Катакомбы (этажи 6-10)
    CAVES = "caves"  # Пещеры (этажи 11-15)
    ABYSS = "abyss"  # Бездна (этажи 16-20)


class Biome:
    """Биом"""
    
    def __init__(
        self,
        biome_type: BiomeType,
        name: str,
        description: str,
        wall_color: Tuple[int, int, int],
        floor_color: Tuple[int, int, int],
        ambient_color: Tuple[int, int, int],
        fog_density: float = 0.0
    ):
        """
        Инициализация биома
        
        Args:
            biome_type: Тип биома
            name: Название
            description: Описание
            wall_color: Цвет стен (RGB)
            floor_color: Цвет пола (RGB)
            ambient_color: Цвет окружения (RGB)
            fog_density: Плотность тумана (0.0 - 1.0)
        """
        self.biome_type = biome_type
        self.name = name
        self.description = description
        self.wall_color = wall_color
        self.floor_color = floor_color
        self.ambient_color = ambient_color
        self.fog_density = fog_density


# Определения биомов
BIOMES = {
    BiomeType.DUNGEON: Biome(
        biome_type=BiomeType.DUNGEON,
        name="Старые лаборатории",
        description="Заброшенные исследовательские помещения НИИЧАВО. Разбитые колбы, книжные полки, незаконченные эксперименты.",
        wall_color=(80, 80, 80),  # Серый камень
        floor_color=(60, 60, 60),  # Тёмно-серый пол
        ambient_color=(100, 100, 100),  # Нейтральное освещение
        fog_density=0.0
    ),
    
    BiomeType.CATACOMBS: Biome(
        biome_type=BiomeType.CATACOMBS,
        name="Архивы и хранилища",
        description="Бесконечные стеллажи с запрещёнными книгами. Магические печати. Кристаллы памяти. Здесь хранятся тайны НИИЧАВО.",
        wall_color=(60, 50, 40),  # Коричневатый камень
        floor_color=(40, 35, 30),  # Тёмный пол
        ambient_color=(70, 60, 50),  # Приглушённое освещение
        fog_density=0.2
    ),
    
    BiomeType.CAVES: Biome(
        biome_type=BiomeType.CAVES,
        name="Экспериментальные зоны",
        description="Активные магические эксперименты. Порталы в другие измерения. Работающие установки. Магическая энергия пульсирует в воздухе.",
        wall_color=(50, 40, 60),  # Фиолетоватый камень
        floor_color=(40, 30, 50),  # Тёмно-фиолетовый пол
        ambient_color=(80, 60, 100),  # Фиолетовое свечение
        fog_density=0.3
    ),
    
    BiomeType.ABYSS: Biome(
        biome_type=BiomeType.ABYSS,
        name="Зона катастрофы",
        description="Эпицентр магической катастрофы. Разрывы пространства-времени. Реальность нестабильна. Здесь произошло что-то ужасное.",
        wall_color=(30, 20, 40),  # Почти чёрный с фиолетовым
        floor_color=(20, 15, 30),  # Очень тёмный пол
        ambient_color=(50, 30, 60),  # Тёмно-фиолетовое свечение
        fog_density=0.5
    )
}


class BiomeManager:
    """Менеджер биомов"""
    
    @staticmethod
    def get_biome_for_floor(floor: int) -> Biome:
        """
        Получить биом для этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Биом
        """
        if floor <= 5:
            return BIOMES[BiomeType.DUNGEON]
        elif floor <= 10:
            return BIOMES[BiomeType.CATACOMBS]
        elif floor <= 15:
            return BIOMES[BiomeType.CAVES]
        else:
            return BIOMES[BiomeType.ABYSS]
    
    @staticmethod
    def get_biome_name(floor: int) -> str:
        """
        Получить название биома для этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Название биома
        """
        biome = BiomeManager.get_biome_for_floor(floor)
        return biome.name
    
    @staticmethod
    def get_biome_description(floor: int) -> str:
        """
        Получить описание биома для этажа
        
        Args:
            floor: Номер этажа
            
        Returns:
            Описание биома
        """
        biome = BiomeManager.get_biome_for_floor(floor)
        return biome.description
    
    @staticmethod
    def get_ambient_effects(floor: int) -> dict:
        """
        Получить эффекты окружения для биома
        
        Args:
            floor: Номер этажа
            
        Returns:
            Словарь с эффектами
        """
        biome = BiomeManager.get_biome_for_floor(floor)
        
        effects = {
            "fog_density": biome.fog_density,
            "ambient_color": biome.ambient_color,
            "lighting_modifier": 1.0 - biome.fog_density * 0.5,  # Темнее с туманом
        }
        
        # Специфичные эффекты для биомов
        if biome.biome_type == BiomeType.CATACOMBS:
            effects["spawn_bones"] = True  # Кости как декорации
            effects["undead_bonus"] = 1.5  # Больше нежити
        
        elif biome.biome_type == BiomeType.CAVES:
            effects["spawn_crystals"] = True  # Светящиеся кристаллы
            effects["spawn_lava"] = True  # Лава
            effects["elemental_bonus"] = 1.5  # Больше элементалей
        
        elif biome.biome_type == BiomeType.ABYSS:
            effects["spawn_portals"] = True  # Телепорты
            effects["reality_distortion"] = True  # Искажение реальности
            effects["demon_bonus"] = 2.0  # Много демонов
        
        return effects


class BiomeDecorator:
    """Декоратор биомов (добавляет специфичные элементы)"""
    
    @staticmethod
    def add_biome_decorations(level, rooms: list, floor: int) -> None:
        """
        Добавить декорации биома на уровень
        
        Args:
            level: Уровень
            rooms: Список комнат
            floor: Номер этажа
        """
        biome = BiomeManager.get_biome_for_floor(floor)
        effects = BiomeManager.get_ambient_effects(floor)
        
        # Катакомбы: добавляем кости
        if effects.get("spawn_bones"):
            BiomeDecorator._add_bones(level, rooms)
        
        # Пещеры: добавляем кристаллы и лаву
        if effects.get("spawn_crystals"):
            BiomeDecorator._add_crystals(level, rooms)
        
        if effects.get("spawn_lava"):
            BiomeDecorator._add_lava_pools(level, rooms)
        
        # Бездна: добавляем порталы
        if effects.get("spawn_portals"):
            BiomeDecorator._add_portals(level, rooms)
    
    @staticmethod
    def _add_bones(level, rooms: list) -> None:
        """Добавить кости как декорации"""
        import random
        
        for room in rooms:
            # 2-4 кости на комнату
            bone_count = random.randint(2, 4)
            
            for _ in range(bone_count):
                x = room.x + random.randint(1, room.width - 2)
                y = room.y + random.randint(1, room.height - 2)
                
                # Кости не блокируют движение (пока просто помечаем)
                # В будущем можно добавить визуальный слой декораций
    
    @staticmethod
    def _add_crystals(level, rooms: list) -> None:
        """Добавить светящиеся кристаллы"""
        import random
        
        for room in rooms:
            # 1-3 кристалла на комнату
            crystal_count = random.randint(1, 3)
            
            for _ in range(crystal_count):
                x = room.x + random.randint(1, room.width - 2)
                y = room.y + random.randint(1, room.height - 2)
                
                # Кристаллы дают освещение (пока просто помечаем)
    
    @staticmethod
    def _add_lava_pools(level, rooms: list) -> None:
        """Добавить лавовые лужи"""
        import random
        
        # 1-2 лавовые лужи на этаж
        pool_count = random.randint(1, 2)
        
        if len(rooms) < 2:
            return
        
        for _ in range(pool_count):
            room = random.choice(rooms[1:])  # Не в первой комнате
            
            # Маленькая лужа (2x2 или 3x3)
            pool_size = random.randint(2, 3)
            
            x = room.x + random.randint(1, room.width - pool_size - 1)
            y = room.y + random.randint(1, room.height - pool_size - 1)
            
            # Лава наносит урон при прохождении (пока просто помечаем)
    
    @staticmethod
    def _add_portals(level, rooms: list) -> None:
        """Добавить телепорты"""
        import random
        
        # 1-3 портала на этаж
        portal_count = random.randint(1, 3)
        
        if len(rooms) < 2:
            return
        
        for _ in range(portal_count):
            room = random.choice(rooms[1:])  # Не в первой комнате
            
            x = room.x + random.randint(1, room.width - 2)
            y = room.y + random.randint(1, room.height - 2)
            
            # Портал телепортирует в случайное место (пока просто помечаем)


if __name__ == "__main__":
    # Тест биомов
    print("🎨 Тест системы биомов\n")
    
    for floor in [1, 5, 8, 12, 18, 20]:
        biome = BiomeManager.get_biome_for_floor(floor)
        effects = BiomeManager.get_ambient_effects(floor)
        
        print(f"Этаж {floor}: {biome.name}")
        print(f"  Описание: {biome.description}")
        print(f"  Туман: {biome.fog_density}")
        print(f"  Эффекты: {list(effects.keys())}")
        print()
