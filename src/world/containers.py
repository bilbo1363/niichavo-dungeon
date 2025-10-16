"""
Система контейнеров (сундуки, ящики, бочки)
"""
from enum import Enum
import pygame
from typing import List, Optional
from ..items.item import Item


class ContainerType(Enum):
    """Типы контейнеров"""
    CHEST = "chest"  # Сундук (деревянный)
    GOLDEN_CHEST = "golden_chest"  # Золотой сундук (редкий)
    BARREL = "barrel"  # Бочка
    CRATE = "crate"  # Ящик
    CORPSE = "corpse"  # Труп искателя
    HIDDEN_STASH = "hidden_stash"  # Тайник


class Container:
    """Контейнер с предметами"""
    
    def __init__(
        self,
        x: int,
        y: int,
        container_type: ContainerType,
        items: List[Item] = None
    ):
        """
        Инициализация контейнера
        
        Args:
            x: Позиция X
            y: Позиция Y
            container_type: Тип контейнера
            items: Список предметов внутри
        """
        self.x = x
        self.y = y
        self.container_type = container_type
        self.items = items if items else []
        self.opened = False
        self.discovered = False  # Для тайников
        
    def open(self) -> List[Item]:
        """
        Открыть контейнер
        
        Returns:
            Список предметов внутри
        """
        if not self.opened:
            self.opened = True
            return self.items
        return []
    
    def is_empty(self) -> bool:
        """Проверить пуст ли контейнер"""
        return len(self.items) == 0
    
    def get_name(self) -> str:
        """Получить название контейнера"""
        names = {
            ContainerType.CHEST: "Сундук",
            ContainerType.GOLDEN_CHEST: "Золотой сундук",
            ContainerType.BARREL: "Бочка",
            ContainerType.CRATE: "Ящик",
            ContainerType.CORPSE: "Труп искателя",
            ContainerType.HIDDEN_STASH: "Тайник",
        }
        return names.get(self.container_type, "Контейнер")
    
    def get_color(self) -> tuple:
        """Получить цвет контейнера"""
        colors = {
            ContainerType.CHEST: (139, 69, 19),  # Коричневый
            ContainerType.GOLDEN_CHEST: (255, 215, 0),  # Золотой
            ContainerType.BARREL: (160, 82, 45),  # Светло-коричневый
            ContainerType.CRATE: (205, 133, 63),  # Бежевый
            ContainerType.CORPSE: (150, 150, 150),  # Серый
            ContainerType.HIDDEN_STASH: (100, 100, 100),  # Тёмно-серый
        }
        return colors.get(self.container_type, (150, 150, 150))
    
    def is_visible(self) -> bool:
        """
        Проверить видим ли контейнер
        
        Returns:
            True если контейнер видим
        """
        # Тайники видны только после обнаружения
        if self.container_type == ContainerType.HIDDEN_STASH:
            return self.discovered
        
        return True
    
    def try_discover(self, chance: float) -> bool:
        """
        Попытка обнаружить тайник
        
        Args:
            chance: Шанс обнаружения (0.0 - 1.0)
            
        Returns:
            True если тайник обнаружен
        """
        if self.container_type != ContainerType.HIDDEN_STASH or self.discovered:
            return False
        
        import random
        if random.random() < chance:
            self.discovered = True
            return True
        
        return False
    
    def render(self, screen: pygame.Surface, camera_x: int, camera_y: int, 
               tile_size: int, fog_of_war=None) -> None:
        """
        Отрисовка контейнера
        
        Args:
            screen: Экран для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            tile_size: Размер тайла
            fog_of_war: Туман войны
        """
        # Проверяем видимость в fog of war
        if fog_of_war and not fog_of_war.is_visible(self.x, self.y):
            return
        
        # Проверяем видим ли контейнер (тайники)
        if not self.is_visible():
            return
        
        screen_x = self.x * tile_size - camera_x
        screen_y = self.y * tile_size - camera_y
        
        color = self.get_color()
        
        # Если открыт - делаем тусклым
        if self.opened:
            color = tuple(c // 2 for c in color)
        
        center_x = screen_x + tile_size // 2
        center_y = screen_y + tile_size // 2
        
        # Рисуем разные формы для разных типов
        if self.container_type in [ContainerType.CHEST, ContainerType.GOLDEN_CHEST]:
            # Сундук - прямоугольник с крышкой
            size = 14
            # Основание
            pygame.draw.rect(
                screen,
                color,
                (center_x - size, center_y - size//2, size * 2, size)
            )
            # Крышка
            if not self.opened:
                pygame.draw.rect(
                    screen,
                    tuple(min(255, c + 30) for c in color),
                    (center_x - size, center_y - size, size * 2, size//2)
                )
            # Обводка
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (center_x - size, center_y - size, size * 2, size * 1.5),
                2
            )
            
        elif self.container_type == ContainerType.BARREL:
            # Бочка - овал
            pygame.draw.ellipse(
                screen,
                color,
                (center_x - 12, center_y - 14, 24, 28)
            )
            pygame.draw.ellipse(
                screen,
                (0, 0, 0),
                (center_x - 12, center_y - 14, 24, 28),
                2
            )
            
        elif self.container_type == ContainerType.CRATE:
            # Ящик - квадрат
            size = 12
            pygame.draw.rect(
                screen,
                color,
                (center_x - size, center_y - size, size * 2, size * 2)
            )
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (center_x - size, center_y - size, size * 2, size * 2),
                2
            )
            # Крестик на ящике
            pygame.draw.line(
                screen,
                (0, 0, 0),
                (center_x - size//2, center_y),
                (center_x + size//2, center_y),
                2
            )
            pygame.draw.line(
                screen,
                (0, 0, 0),
                (center_x, center_y - size//2),
                (center_x, center_y + size//2),
                2
            )
            
        elif self.container_type == ContainerType.CORPSE:
            # Труп - крестик
            size = 10
            # Горизонтальная линия
            pygame.draw.line(
                screen,
                color,
                (center_x - size, center_y),
                (center_x + size, center_y),
                4
            )
            # Вертикальная линия
            pygame.draw.line(
                screen,
                color,
                (center_x, center_y - size//2),
                (center_x, center_y + size),
                4
            )
            
        elif self.container_type == ContainerType.HIDDEN_STASH:
            # Тайник - маленький квадрат с вопросом
            size = 10
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
            # Вопросительный знак
            font = pygame.font.Font(None, 20)
            text = font.render("?", True, (255, 255, 0))
            text_rect = text.get_rect(center=(center_x, center_y))
            screen.blit(text, text_rect)
