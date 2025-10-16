"""
Система рун
"""
from dataclasses import dataclass
from enum import Enum
import pygame


class RuneType(Enum):
    """Типы рун"""
    STABILITY = "stability"  # Руна устойчивости (основная)
    FIRE = "fire"           # Огненная руна
    ICE = "ice"             # Ледяная руна
    LIGHTNING = "lightning" # Молниевая руна
    EARTH = "earth"         # Земляная руна


@dataclass
class Rune:
    """Класс руны"""
    
    rune_type: RuneType
    x: int
    y: int
    collected: bool = False
    
    # Визуальные параметры
    color: tuple = (255, 215, 0)  # Золотой по умолчанию
    size: int = 20
    
    def __post_init__(self):
        """Инициализация после создания"""
        # Устанавливаем цвет в зависимости от типа
        if self.rune_type == RuneType.STABILITY:
            self.color = (255, 215, 0)  # Золотой
        elif self.rune_type == RuneType.FIRE:
            self.color = (255, 69, 0)   # Красно-оранжевый
        elif self.rune_type == RuneType.ICE:
            self.color = (0, 191, 255)  # Голубой
        elif self.rune_type == RuneType.LIGHTNING:
            self.color = (255, 255, 0)  # Желтый
        elif self.rune_type == RuneType.EARTH:
            self.color = (139, 69, 19)  # Коричневый
            
    def collect(self) -> None:
        """Собрать руну"""
        if not self.collected:
            self.collected = True
            print(f"✨ Собрана руна: {self.rune_type.value}")
            
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка руны
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны для проверки видимости
        """
        if self.collected:
            return  # Не рисуем собранную руну
            
        # Проверяем видимость через fog of war
        if fog_of_war and not fog_of_war.is_visible(self.x, self.y):
            return  # Не рисуем если не видно
            
        # Вычисляем позицию на экране (центр клетки)
        tile_size = 32
        screen_x = self.x * tile_size - camera_x + tile_size // 2
        screen_y = self.y * tile_size - camera_y + tile_size // 2
        
        # Рисуем руну как ромб (diamond)
        points = [
            (screen_x, screen_y - self.size),      # Верх
            (screen_x + self.size, screen_y),      # Право
            (screen_x, screen_y + self.size),      # Низ
            (screen_x - self.size, screen_y)       # Лево
        ]
        
        # Заливка
        pygame.draw.polygon(screen, self.color, points)
        
        # Контур
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        
        # Эффект свечения (пульсация)
        import math
        import time
        pulse = abs(math.sin(time.time() * 3)) * 0.3 + 0.7
        glow_color = tuple(int(c * pulse) for c in self.color)
        
        # Внешний контур свечения
        glow_points = [
            (screen_x, screen_y - self.size - 3),
            (screen_x + self.size + 3, screen_y),
            (screen_x, screen_y + self.size + 3),
            (screen_x - self.size - 3, screen_y)
        ]
        pygame.draw.polygon(screen, glow_color, glow_points, 1)


class RuneManager:
    """Менеджер рун на уровне"""
    
    def __init__(self):
        """Инициализация менеджера рун"""
        self.runes: list[Rune] = []
        
    def add_rune(self, rune: Rune) -> None:
        """
        Добавить руну
        
        Args:
            rune: Руна для добавления
        """
        self.runes.append(rune)
        
    def spawn_stability_rune(self, x: int, y: int) -> Rune:
        """
        Создать руну устойчивости
        
        Args:
            x: Позиция X
            y: Позиция Y
            
        Returns:
            Созданная руна
        """
        rune = Rune(RuneType.STABILITY, x, y)
        self.add_rune(rune)
        print(f"🔮 Руна устойчивости появилась на ({x}, {y})")
        return rune
        
    def check_collection(self, player_x: int, player_y: int) -> list[Rune]:
        """
        Проверить сбор рун игроком
        
        Args:
            player_x: Позиция игрока X
            player_y: Позиция игрока Y
            
        Returns:
            Список собранных рун
        """
        collected = []
        
        for rune in self.runes:
            if not rune.collected and rune.x == player_x and rune.y == player_y:
                rune.collect()
                collected.append(rune)
                
        return collected
        
    def get_uncollected_count(self) -> int:
        """
        Получить количество несобранных рун
        
        Returns:
            Количество несобранных рун
        """
        return sum(1 for rune in self.runes if not rune.collected)
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка всех рун
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны для проверки видимости
        """
        for rune in self.runes:
            rune.render(screen, camera_x, camera_y, fog_of_war)


if __name__ == "__main__":
    # Тест системы рун
    manager = RuneManager()
    
    # Создаём руну устойчивости
    rune = manager.spawn_stability_rune(10, 10)
    print(f"Руна создана: {rune.rune_type.value}")
    print(f"Цвет: {rune.color}")
    
    # Проверяем сбор
    collected = manager.check_collection(10, 10)
    print(f"Собрано рун: {len(collected)}")
    print(f"Несобранных рун: {manager.get_uncollected_count()}")
