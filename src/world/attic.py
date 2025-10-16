"""
Чердак - стартовая локация
"""
import numpy as np
import pygame
from typing import Tuple, Optional
from .storage import Storage


class Attic:
    """Класс чердака (стартовая локация)"""
    
    # Типы тайлов
    TILE_FLOOR = 0
    TILE_WALL = 1
    TILE_ENTRANCE = 2  # Вход в подземелье
    TILE_STORAGE = 3   # Хранилище
    
    # Цвета
    COLOR_FLOOR = (139, 90, 43)      # Деревянный пол
    COLOR_WALL = (101, 67, 33)       # Деревянные стены
    COLOR_ENTRANCE = (200, 50, 50)   # Красный люк
    COLOR_STORAGE = (150, 150, 50)   # Желтый сундук
    
    def __init__(self, width: int = 30, height: int = 20):
        """
        Инициализация чердака
        
        Args:
            width: Ширина чердака
            height: Высота чердака
        """
        self.width = width
        self.height = height
        self.tile_size = 32
        
        # Создаём сетку чердака
        self.tiles = np.zeros((height, width), dtype=np.uint8)
        
        # Позиции
        self.entrance_pos: Optional[Tuple[int, int]] = None  # Вход в подземелье
        self.storage_pos: Optional[Tuple[int, int]] = None   # Хранилище
        self.spawn_pos: Optional[Tuple[int, int]] = None     # Точка появления игрока
        
        # Хранилище (сундук)
        self.storage = Storage(max_slots=50)
        
        # Генерируем чердак
        self._generate()
        
        print(f"🏠 Чердак создан: {width}x{height}")
        
    def _generate(self) -> None:
        """Генерация чердака"""
        # Заполняем полом
        self.tiles.fill(self.TILE_FLOOR)
        
        # Создаём стены по периметру
        self.tiles[0, :] = self.TILE_WALL
        self.tiles[-1, :] = self.TILE_WALL
        self.tiles[:, 0] = self.TILE_WALL
        self.tiles[:, -1] = self.TILE_WALL
        
        # Вход в подземелье (люк в центре)
        entrance_x = self.width // 2
        entrance_y = self.height // 2 + 3
        self.tiles[entrance_y, entrance_x] = self.TILE_ENTRANCE
        self.entrance_pos = (entrance_x, entrance_y)
        
        # Хранилище (сундук в углу)
        storage_x = self.width - 3
        storage_y = 2
        self.tiles[storage_y, storage_x] = self.TILE_STORAGE
        self.storage_pos = (storage_x, storage_y)
        
        # Точка появления игрока (перед люком)
        self.spawn_pos = (entrance_x, entrance_y - 2)
        
        # Добавляем декоративные элементы (столбы)
        for x in [5, self.width - 6]:
            for y in [5, self.height - 6]:
                if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                    self.tiles[y, x] = self.TILE_WALL
                    
        print(f"   Вход в подземелье: {self.entrance_pos}")
        print(f"   Хранилище: {self.storage_pos}")
        print(f"   Точка появления: {self.spawn_pos}")
        
    def is_walkable(self, x: int, y: int) -> bool:
        """
        Проверить, можно ли пройти через клетку
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            True если можно пройти
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
            
        tile = self.tiles[y, x]
        return tile in [self.TILE_FLOOR, self.TILE_ENTRANCE, self.TILE_STORAGE]
        
    def get_tile(self, x: int, y: int) -> int:
        """
        Получить тип тайла
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            Тип тайла
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return self.TILE_WALL
        return self.tiles[y, x]
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """
        Отрисовка чердака
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        screen_width, screen_height = screen.get_size()
        
        start_x = max(0, camera_x // self.tile_size)
        start_y = max(0, camera_y // self.tile_size)
        end_x = min(self.width, (camera_x + screen_width) // self.tile_size + 1)
        end_y = min(self.height, (camera_y + screen_height) // self.tile_size + 1)
        
        # Отрисовываем тайлы
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y, x]
                
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                
                # Выбираем цвет
                if tile_type == self.TILE_WALL:
                    color = self.COLOR_WALL
                elif tile_type == self.TILE_ENTRANCE:
                    color = self.COLOR_ENTRANCE
                elif tile_type == self.TILE_STORAGE:
                    color = self.COLOR_STORAGE
                else:
                    color = self.COLOR_FLOOR
                    
                # Рисуем тайл
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x, screen_y, self.tile_size, self.tile_size)
                )
                
                # Рисуем сетку
                pygame.draw.rect(
                    screen,
                    (30, 30, 30),
                    (screen_x, screen_y, self.tile_size, self.tile_size),
                    1
                )
                
        # Рисуем иконки
        self._render_icons(screen, camera_x, camera_y)
        
    def _render_icons(self, screen: pygame.Surface, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка иконок на чердаке
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        # Иконка входа в подземелье (стрелка вниз)
        if self.entrance_pos:
            ent_x, ent_y = self.entrance_pos
            screen_x = ent_x * self.tile_size - camera_x + self.tile_size // 2
            screen_y = ent_y * self.tile_size - camera_y + self.tile_size // 2
            
            # Треугольник вниз
            points = [
                (screen_x, screen_y + 10),      # Низ
                (screen_x - 8, screen_y - 10),  # Верх-лево
                (screen_x + 8, screen_y - 10)   # Верх-право
            ]
            pygame.draw.polygon(screen, (255, 255, 255), points)
            
        # Иконка хранилища (сундук)
        if self.storage_pos:
            stor_x, stor_y = self.storage_pos
            screen_x = stor_x * self.tile_size - camera_x
            screen_y = stor_y * self.tile_size - camera_y
            
            # Рисуем простой сундук
            pygame.draw.rect(
                screen,
                (101, 67, 33),
                (screen_x + 6, screen_y + 10, 20, 14)
            )
            pygame.draw.rect(
                screen,
                (139, 90, 43),
                (screen_x + 6, screen_y + 6, 20, 8)
            )
            # Замок
            pygame.draw.circle(
                screen,
                (255, 215, 0),
                (screen_x + 16, screen_y + 16),
                3
            )


if __name__ == "__main__":
    # Тест чердака
    attic = Attic()
    print(f"Размер: {attic.width}x{attic.height}")
    print(f"Клетка (15, 10) проходима: {attic.is_walkable(15, 10)}")
    print(f"Клетка (0, 0) проходима: {attic.is_walkable(0, 0)}")
