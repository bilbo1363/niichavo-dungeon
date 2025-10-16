"""
Система спавна предметов на уровнях
"""
import random
from typing import List, Tuple, Optional
from .item import Item, ItemDatabase, ItemType, ItemRarity
import pygame


class ItemSpawn:
    """Предмет на карте"""
    
    def __init__(self, item: Item, x: int, y: int):
        """
        Инициализация предмета на карте
        
        Args:
            item: Предмет
            x: Позиция X
            y: Позиция Y
        """
        self.item = item
        self.x = x
        self.y = y
        self.picked_up = False
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка предмета
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны
        """
        if self.picked_up:
            return
            
        # Проверяем видимость
        if fog_of_war and not fog_of_war.is_visible(self.x, self.y):
            return
            
        # Вычисляем позицию на экране
        tile_size = 32
        screen_x = self.x * tile_size - camera_x + tile_size // 2
        screen_y = self.y * tile_size - camera_y + tile_size // 2
        
        # Цвет по редкости
        color = self.item.get_rarity_color()
        
        # Рисуем предмет как квадрат
        size = 8
        pygame.draw.rect(
            screen,
            color,
            (screen_x - size, screen_y - size, size * 2, size * 2)
        )
        
        # Контур
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (screen_x - size, screen_y - size, size * 2, size * 2),
            1
        )


class ItemSpawner:
    """Генератор предметов на уровнях"""
    
    def __init__(self):
        """Инициализация генератора"""
        self.item_db = ItemDatabase()
        self.spawned_items: List[ItemSpawn] = []
        
    def spawn_random_items(self, level, floor_number: int, count: int = 3) -> None:
        """
        Создать случайные предметы на уровне
        
        Args:
            level: Уровень
            floor_number: Номер этажа
            count: Количество предметов
        """
        # Определяем какие предметы могут появиться на этом этаже
        possible_items = self._get_possible_items(floor_number)
        
        if not possible_items:
            return
            
        spawned = 0
        attempts = 0
        max_attempts = count * 10
        
        while spawned < count and attempts < max_attempts:
            attempts += 1
            
            # Случайная позиция
            x = random.randint(1, level.width - 2)
            y = random.randint(1, level.height - 2)
            
            # Проверяем что это пол и не занято
            if level.get_tile(x, y) != level.TILE_FLOOR:
                continue
                
            # Проверяем что не на входе/выходе
            if (x, y) == level.entrance_pos or (x, y) == level.exit_pos:
                continue
                
            # Проверяем что не занято другим предметом
            if any(item.x == x and item.y == y and not item.picked_up for item in self.spawned_items):
                continue
                
            # Выбираем случайный предмет
            item_id = random.choice(possible_items)
            item = self.item_db.get_item(item_id)
            
            if item:
                item_spawn = ItemSpawn(item, x, y)
                self.spawned_items.append(item_spawn)
                spawned += 1
                
        print(f"📦 Создано {spawned} предметов на этаже {floor_number}")
        
    def _get_possible_items(self, floor_number: int) -> List[str]:
        """
        Получить список возможных предметов для этажа
        
        Args:
            floor_number: Номер этажа
            
        Returns:
            Список ID предметов
        """
        items = []
        
        # Базовые расходники (всегда доступны)
        items.extend(["bandage", "energy_drink", "coffee"])
        
        # ЕДА (часто встречается)
        food_items = ["bread", "canned_food", "apple", "water_bottle", "chocolate"]
        items.extend(random.sample(food_items, k=min(3, len(food_items))))
        
        # Более редкая еда
        if random.random() < 0.4:
            items.append("dried_meat")
        if random.random() < 0.3:
            items.append("protein_bar")
        if random.random() < 0.2:
            items.append("hot_meal")
        
        # Напитки
        if random.random() < 0.5:
            items.append("tea")
        if random.random() < 0.4:
            items.append("juice")
        
        # Аптечки реже
        if random.random() < 0.3:
            items.append("medkit")
            
        # Оружие в зависимости от глубины
        if floor_number <= 5:
            items.extend(["rusty_pipe", "crowbar"])
        elif floor_number <= 10:
            items.extend(["crowbar", "fire_axe"])
        else:
            items.extend(["fire_axe"])
            
        # Ключевые предметы на глубоких этажах
        if floor_number >= 10:
            if random.random() < 0.1:
                items.append("flashlight")
            if random.random() < 0.05:
                items.append("master_key")
                
        return items
        
    def check_pickup(self, player_x: int, player_y: int, player, manual: bool = False) -> Optional[Item]:
        """
        Проверить подбор предмета
        
        Args:
            player_x: Позиция игрока X
            player_y: Позиция игрока Y
            player: Игрок
            manual: Если True, подбор только по нажатию клавиши
            
        Returns:
            Поднятый предмет или None
        """
        for item_spawn in self.spawned_items:
            if item_spawn.picked_up:
                continue
                
            if item_spawn.x == player_x and item_spawn.y == player_y:
                # Если manual=True, не подбираем автоматически
                if not manual:
                    return None
                
                # Пытаемся добавить в инвентарь
                if player.inventory.add_item(item_spawn.item):
                    item_spawn.picked_up = True
                    return item_spawn.item
                else:
                    print("❌ Инвентарь полон!")
                    
        return None
    
    def has_item_at(self, x: int, y: int) -> bool:
        """
        Проверить есть ли предмет на позиции
        
        Args:
            x: Позиция X
            y: Позиция Y
            
        Returns:
            True если есть предмет
        """
        for item_spawn in self.spawned_items:
            if not item_spawn.picked_up and item_spawn.x == x and item_spawn.y == y:
                return True
        return False
        
    def render_all(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка всех предметов
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны
        """
        for item_spawn in self.spawned_items:
            item_spawn.render(screen, camera_x, camera_y, fog_of_war)
            
    def clear(self) -> None:
        """Очистить все предметы"""
        self.spawned_items.clear()
    
    def spawn_dropped_item(self, item: Item, x: int, y: int, quantity: int = 1) -> None:
        """
        Разместить выброшенный предмет на карте
        
        Args:
            item: Предмет
            x: Позиция X
            y: Позиция Y
            quantity: Количество (для стакающихся предметов)
        """
        # Создаём копию предмета
        from copy import deepcopy
        dropped_item = deepcopy(item)
        
        # Создаём спавн на карте
        item_spawn = ItemSpawn(dropped_item, x, y)
        self.spawned_items.append(item_spawn)
        
        print(f"📍 Предмет размещён на карте: {item.name} x{quantity} на ({x}, {y})")


if __name__ == "__main__":
    # Тест спавнера
    spawner = ItemSpawner()
    
    # Тестируем получение предметов для разных этажей
    for floor in [1, 5, 10, 15, 20]:
        items = spawner._get_possible_items(floor)
        print(f"\nЭтаж {floor}: {items}")
