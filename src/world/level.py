"""
Класс уровня
"""
import numpy as np
import pygame
from typing import Tuple
from .fog_of_war import FogOfWar
from ..items.rune import RuneManager
from ..puzzles.riddle import RiddleManager
from ..items.item_spawner import ItemSpawner
from ..entities.enemy_spawner import EnemySpawner


class Level:
    """Класс уровня"""
    
    # Типы тайлов
    TILE_FLOOR = 0
    TILE_WALL = 1
    
    # Цвета тайлов (по умолчанию, будут переопределены биомом)
    COLOR_FLOOR = (50, 50, 50)      # Темно-серый
    COLOR_WALL = (100, 100, 100)    # Светло-серый
    
    def __init__(self, width: int = 60, height: int = 40, floor_number: int = 1):
        """
        Инициализация уровня
        
        Args:
            width: Ширина в клетках
            height: Высота в клетках
            floor_number: Номер этажа (для определения биома)
        """
        self.width = width
        self.height = height
        self.tile_size = 32
        self.floor_number = floor_number
        
        # Создаём сетку уровня (NumPy массив)
        self.tiles = np.zeros((height, width), dtype=np.uint8)
        
        # Позиции входа и выхода
        self.entrance_pos = None  # (x, y)
        self.exit_pos = None      # (x, y)
        
        # Fog of War
        self.fog_of_war = FogOfWar(width, height)
        
        # Есть ли свет на этаже (некоторые этажи темные)
        self.has_light = True
        
        # Применяем цвета биома
        self._apply_biome_colors()
        
        # Менеджер рун
        self.rune_manager = RuneManager()
        
        # Менеджер загадок
        self.riddle_manager = RiddleManager()
        
        # Спавнер предметов
        self.item_spawner = ItemSpawner()
        
        # Спавнер врагов
        self.enemy_spawner = EnemySpawner()
        
        # Препятствия (будут добавлены генератором)
        self.obstacles = []
        
        # Ловушки (будут добавлены генератором)
        self.traps = []
        
        # Записки (будут добавлены генератором)
        self.notes = []
        
        # Контейнеры (будут добавлены генератором)
        self.containers = []
        
        # Интерактивные объекты (доски с записками, кости путешественников)
        self.interactive_objects = []
        
        print(f"🗺️  Уровень создан: {width}x{height}")
        
    def _generate_test_level(self) -> None:
        """Генерация простого тестового уровня"""
        # Заполняем всё полом
        self.tiles.fill(self.TILE_FLOOR)
        
        # Создаём границы (стены)
        self.tiles[0, :] = self.TILE_WALL      # Верхняя граница
        self.tiles[-1, :] = self.TILE_WALL     # Нижняя граница
        self.tiles[:, 0] = self.TILE_WALL      # Левая граница
        self.tiles[:, -1] = self.TILE_WALL     # Правая граница
        
        # Добавим несколько препятствий для теста
        # Вертикальная стена
        for y in range(10, 20):
            self.tiles[y, 20] = self.TILE_WALL
            
        # Горизонтальная стена
        for x in range(30, 40):
            self.tiles[15, x] = self.TILE_WALL
            
        print("✅ Тестовый уровень сгенерирован")
        
    def is_walkable(self, x: int, y: int) -> bool:
        """
        Проверка, можно ли пройти на клетку
        
        Args:
            x: Позиция X
            y: Позиция Y
            
        Returns:
            True если можно пройти
        """
        # Проверка границ
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
            
        # Проверка типа тайла
        if self.tiles[y, x] != self.TILE_FLOOR:
            return False
        
        # Проверка препятствий
        for obstacle in self.obstacles:
            if obstacle.x == x and obstacle.y == y and obstacle.blocks_movement:
                return False
        
        return True
        
    def get_tile(self, x: int, y: int) -> int:
        """
        Получить тип тайла
        
        Args:
            x: Позиция X
            y: Позиция Y
            x: Координата X
            y: Координата Y
            
        Returns:
            Тип тайла
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return self.TILE_WALL
        return self.tiles[y, x]
        
    def update_fog_of_war(self, player_x: int, player_y: int) -> None:
        """
        Обновить туман войны
        
        Args:
            player_x: Позиция игрока X
            player_y: Позиция игрока Y
        """
        self.fog_of_war.update_vision(player_x, player_y, self.tiles)
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """
        Отрисовка уровня
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        # Вычисляем видимую область
        screen_width, screen_height = screen.get_size()
        
        start_x = max(0, camera_x // self.tile_size)
        start_y = max(0, camera_y // self.tile_size)
        end_x = min(self.width, (camera_x + screen_width) // self.tile_size + 1)
        end_y = min(self.height, (camera_y + screen_height) // self.tile_size + 1)
        
        # Отрисовываем только видимые тайлы
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Проверяем видимость
                visibility = self.fog_of_war.get_visibility(x, y)
                
                # Если не исследовано - не рисуем
                if visibility == FogOfWar.UNEXPLORED:
                    continue
                
                tile_type = self.tiles[y, x]
                
                # Вычисляем позицию на экране
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                
                # Выбираем цвет
                if tile_type == self.TILE_WALL:
                    base_color = self.COLOR_WALL
                else:
                    base_color = self.COLOR_FLOOR
                
                # Затемняем если не видимо сейчас
                if visibility == FogOfWar.EXPLORED:
                    # Исследовано, но не видимо - затемняем
                    color = tuple(c // 2 for c in base_color)
                else:
                    # Видимо сейчас - полный цвет
                    color = base_color
                    
                # Рисуем тайл
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x, screen_y, self.tile_size, self.tile_size)
                )
                
                # Рисуем сетку (для отладки)
                if visibility == FogOfWar.VISIBLE:
                    pygame.draw.rect(
                        screen,
                        (30, 30, 30),
                        (screen_x, screen_y, self.tile_size, self.tile_size),
                        1
                    )
                
        # Отрисовываем вход (зелёный) - только если видимо
        if self.entrance_pos:
            ent_x, ent_y = self.entrance_pos
            if self.fog_of_war.is_visible(ent_x, ent_y):
                screen_x = ent_x * self.tile_size - camera_x
                screen_y = ent_y * self.tile_size - camera_y
                pygame.draw.circle(
                    screen,
                    (0, 255, 0),
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    self.tile_size // 3
                )
            
        # Отрисовываем выход (красный) - только если видимо
        if self.exit_pos:
            exit_x, exit_y = self.exit_pos
            if self.fog_of_war.is_visible(exit_x, exit_y):
                screen_x = exit_x * self.tile_size - camera_x
                screen_y = exit_y * self.tile_size - camera_y
                pygame.draw.circle(
                    screen,
                    (255, 0, 0),
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    self.tile_size // 3
                )
                
        # Отрисовываем препятствия (с проверкой fog of war)
        self._render_obstacles(screen, camera_x, camera_y)
        
        # Отрисовываем ловушки (с проверкой fog of war)
        self._render_traps(screen, camera_x, camera_y)
        
        # Отрисовываем записки (с проверкой fog of war)
        self._render_notes(screen, camera_x, camera_y)
        
        # Отрисовываем контейнеры (с проверкой fog of war)
        self._render_containers(screen, camera_x, camera_y)
        
        # Отрисовываем интерактивные объекты (доски и кости)
        self._render_interactive_objects(screen, camera_x, camera_y)
        
        # Отрисовываем руны (с проверкой fog of war)
        self.rune_manager.render(screen, camera_x, camera_y, self.fog_of_war)
        
        # Отрисовываем загадки (с проверкой fog of war)
        self.riddle_manager.render(screen, camera_x, camera_y, self.fog_of_war)
        
        # Отрисовываем предметы (с проверкой fog of war)
        self.item_spawner.render_all(screen, camera_x, camera_y, self.fog_of_war)
        
        # Отрисовываем врагов (с проверкой fog of war)
        self.enemy_spawner.render_all(screen, camera_x, camera_y, self.fog_of_war)
    
    def _render_obstacles(self, screen, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка препятствий
        
        Args:
            screen: Экран для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        from .obstacles import ObstacleType
        
        # Цвета для разных типов препятствий
        obstacle_colors = {
            ObstacleType.PILLAR: (120, 120, 120),  # Серый
            ObstacleType.TABLE: (139, 69, 19),  # Коричневый
            ObstacleType.STATUE: (160, 160, 160),  # Светло-серый
            ObstacleType.RUBBLE: (100, 100, 100),  # Тёмно-серый
            ObstacleType.PIT: (20, 20, 20),  # Почти чёрный
            ObstacleType.WATER: (0, 100, 200),  # Синий
            ObstacleType.LAVA: (255, 100, 0),  # Оранжевый
        }
        
        for obstacle in self.obstacles:
            # Проверяем видимость
            if not self.fog_of_war.is_visible(obstacle.x, obstacle.y):
                continue
            
            screen_x = obstacle.x * self.tile_size - camera_x
            screen_y = obstacle.y * self.tile_size - camera_y
            
            # Получаем цвет препятствия
            color = obstacle_colors.get(obstacle.obstacle_type, (100, 100, 100))
            
            # Рисуем препятствие
            if obstacle.obstacle_type == ObstacleType.PILLAR:
                # Колонна - круг
                pygame.draw.circle(
                    screen,
                    color,
                    (screen_x + self.tile_size // 2, screen_y + self.tile_size // 2),
                    self.tile_size // 3
                )
            elif obstacle.obstacle_type in [ObstacleType.WATER, ObstacleType.LAVA]:
                # Вода/лава - полупрозрачный квадрат
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x, screen_y, self.tile_size, self.tile_size)
                )
            else:
                # Остальные - квадрат
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x + 4, screen_y + 4, self.tile_size - 8, self.tile_size - 8)
                )
    
    def _render_notes(self, screen, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка записок
        
        Args:
            screen: Экран для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        for note in self.notes:
            # Проверяем видимость
            if not self.fog_of_war.is_visible(note.x, note.y):
                continue
            
            screen_x = note.x * self.tile_size - camera_x
            screen_y = note.y * self.tile_size - camera_y
            
            # Цвет зависит от типа записки
            if note.read:
                color = (150, 150, 150)  # Серый если прочитана
            else:
                color = (255, 220, 150)  # Жёлтый если не прочитана
            
            # Рисуем записку как прямоугольник с символом
            pygame.draw.rect(
                screen,
                color,
                (screen_x + 8, screen_y + 8, self.tile_size - 16, self.tile_size - 16)
            )
            
            # Рисуем рамку
            pygame.draw.rect(
                screen,
                (100, 100, 100),
                (screen_x + 8, screen_y + 8, self.tile_size - 16, self.tile_size - 16),
                2
            )
            
            # Рисуем символ "📜" (упрощённо - линии)
            pygame.draw.line(
                screen,
                (50, 50, 50),
                (screen_x + 12, screen_y + 14),
                (screen_x + self.tile_size - 12, screen_y + 14),
                2
            )
            pygame.draw.line(
                screen,
                (50, 50, 50),
                (screen_x + 12, screen_y + 18),
                (screen_x + self.tile_size - 12, screen_y + 18),
                2
            )
    
    def _render_traps(self, screen, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка ловушек
        
        Args:
            screen: Экран для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        from .traps import TrapType
        
        # Цвета для разных типов ловушек
        trap_colors = {
            TrapType.SPIKES: (150, 150, 150),  # Серый
            TrapType.ARROW: (139, 69, 19),  # Коричневый
            TrapType.FIRE: (255, 100, 0),  # Оранжевый
            TrapType.ICE: (100, 200, 255),  # Голубой
            TrapType.TELEPORT: (200, 100, 255),  # Фиолетовый
            TrapType.POISON: (100, 200, 100),  # Зелёный
            TrapType.COLLAPSE: (100, 100, 100),  # Тёмно-серый
            TrapType.EXPLOSIVE: (255, 50, 50),  # Красный
        }
        
        for trap in self.traps:
            # Проверяем видимость в fog of war
            if not self.fog_of_war.is_visible(trap.x, trap.y):
                continue
            
            # Проверяем видима ли ловушка (скрытые невидимы до обнаружения)
            if not trap.is_visible():
                continue
            
            # Не показываем сработавшие одноразовые ловушки
            if trap.triggered and trap.trap_type not in [TrapType.FIRE, TrapType.ICE, TrapType.POISON]:
                continue
            
            screen_x = trap.x * self.tile_size - camera_x
            screen_y = trap.y * self.tile_size - camera_y
            
            # Получаем цвет ловушки
            color = trap_colors.get(trap.trap_type, (200, 200, 0))
            
            # Если ловушка сработала - делаем полупрозрачной
            if trap.triggered:
                color = tuple(c // 2 for c in color)
            
            # Если ловушка обнаружена но не сработала - делаем тусклой
            if trap.detected and not trap.triggered:
                color = tuple(c * 2 // 3 for c in color)
            
            center_x = screen_x + self.tile_size // 2
            center_y = screen_y + self.tile_size // 2
            
            # ВИДИМЫЕ МЕХАНИЗМЫ - рисуем как квадраты
            if not trap.is_hidden:
                size = 12
                pygame.draw.rect(
                    screen,
                    color,
                    (center_x - size, center_y - size, size * 2, size * 2)
                )
                pygame.draw.rect(
                    screen,
                    (255, 255, 0),
                    (center_x - size, center_y - size, size * 2, size * 2),
                    2
                )
            # СКРЫТЫЕ ЛОВУШКИ (обнаруженные) - рисуем как треугольники
            else:
                size = 10
                # Треугольник
                points = [
                    (center_x, center_y - size),  # Верх
                    (center_x - size, center_y + size),  # Левый нижний
                    (center_x + size, center_y + size),  # Правый нижний
                ]
                
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (255, 255, 0), points, 2)  # Жёлтая обводка
                
                # Восклицательный знак в центре
                pygame.draw.line(
                    screen,
                    (0, 0, 0),
                    (center_x, center_y - 4),
                    (center_x, center_y + 2),
                    2
                )
                pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y + 5), 1)
    
    def _render_containers(self, screen, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка контейнеров
        
        Args:
            screen: Экран для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        for container in self.containers:
            container.render(screen, camera_x, camera_y, self.tile_size, self.fog_of_war)
    
    def _apply_biome_colors(self) -> None:
        """Применить цвета биома к уровню"""
        try:
            from .biomes import BiomeManager
            
            biome = BiomeManager.get_biome_for_floor(self.floor_number)
            
            # Обновляем цвета тайлов
            Level.COLOR_FLOOR = biome.floor_color
            Level.COLOR_WALL = biome.wall_color
            
            # Применяем эффекты освещения
            if biome.fog_density > 0.3:
                self.has_light = False  # Темнее на глубоких этажах
                
        except ImportError:
            # Если модуль биомов не найден, используем стандартные цвета
            pass
    
    def _render_interactive_objects(self, screen: pygame.Surface, camera_x: int, camera_y: int) -> None:
        """
        Отрисовка интерактивных объектов (доски и кости)
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        # Получаем менеджер спрайтов
        from ..graphics.sprite_manager import SpriteManager
        sprite_manager = SpriteManager()
        
        for obj in self.interactive_objects:
            # Проверяем видимость в fog of war
            if not self.fog_of_war.is_visible(obj.x, obj.y):
                continue
            
            screen_x = obj.x * self.tile_size - camera_x
            screen_y = obj.y * self.tile_size - camera_y
            
            # Получаем спрайт объекта
            sprite = obj.get_sprite(sprite_manager)
            
            if sprite:
                # Рисуем спрайт
                screen.blit(sprite, (screen_x, screen_y))
            else:
                # Fallback - рисуем как раньше
                color = obj.get_color()
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x + 4, screen_y + 4, self.tile_size - 8, self.tile_size - 8)
                )
                
                font = pygame.font.Font(None, 28)
                symbol = obj.get_display_char()
                text = font.render(symbol, True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_x + self.tile_size // 2, screen_y + self.tile_size // 2))
                screen.blit(text, text_rect)


if __name__ == "__main__":
    # Тест класса Level
    level = Level(60, 40)
    print(f"Размер: {level.width}x{level.height}")
    print(f"Клетка (10, 10) проходима: {level.is_walkable(10, 10)}")
    print(f"Клетка (0, 0) проходима: {level.is_walkable(0, 0)}")
