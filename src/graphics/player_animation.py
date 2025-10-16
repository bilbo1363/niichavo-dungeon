"""
Анимация игрока
"""
import pygame
from typing import Tuple


class PlayerAnimation:
    """Анимация игрока"""
    
    def __init__(self, tile_size: int = 32):
        """
        Инициализация анимации
        
        Args:
            tile_size: Размер тайла
        """
        self.tile_size = tile_size
        self.current_direction = "down"  # down, up, left, right
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.15  # Секунд на кадр
        self.is_moving = False
        
        # Создаём спрайты для каждого направления
        self._create_sprites()
    
    def _create_sprites(self) -> None:
        """Создать пиксельные спрайты игрока"""
        self.sprites = {
            "down": self._create_down_sprites(),
            "up": self._create_up_sprites(),
            "left": self._create_left_sprites(),
            "right": self._create_right_sprites(),
        }
    
    def _create_down_sprites(self) -> list:
        """Создать спрайты для движения вниз (3 кадра)"""
        sprites = []
        
        # Кадр 1: стоя
        surf1 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf1, (0, 100, 200))  # Синий
        sprites.append(surf1)
        
        # Кадр 2: левая нога вперёд
        surf2 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf2, (0, 100, 200), leg_offset=-2)
        sprites.append(surf2)
        
        # Кадр 3: правая нога вперёд
        surf3 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf3, (0, 100, 200), leg_offset=2)
        sprites.append(surf3)
        
        return sprites
    
    def _create_up_sprites(self) -> list:
        """Создать спрайты для движения вверх (3 кадра)"""
        sprites = []
        
        # Кадр 1: стоя
        surf1 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf1, (0, 100, 200), facing_up=True)
        sprites.append(surf1)
        
        # Кадр 2: левая нога вперёд
        surf2 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf2, (0, 100, 200), facing_up=True, leg_offset=-2)
        sprites.append(surf2)
        
        # Кадр 3: правая нога вперёд
        surf3 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf3, (0, 100, 200), facing_up=True, leg_offset=2)
        sprites.append(surf3)
        
        return sprites
    
    def _create_left_sprites(self) -> list:
        """Создать спрайты для движения влево (3 кадра)"""
        sprites = []
        
        # Кадр 1: стоя
        surf1 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf1, (0, 100, 200), facing_left=True)
        sprites.append(surf1)
        
        # Кадр 2: нога вперёд
        surf2 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf2, (0, 100, 200), facing_left=True, leg_offset=-2)
        sprites.append(surf2)
        
        # Кадр 3: нога назад
        surf3 = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        self._draw_player_body(surf3, (0, 100, 200), facing_left=True, leg_offset=2)
        sprites.append(surf3)
        
        return sprites
    
    def _create_right_sprites(self) -> list:
        """Создать спрайты для движения вправо (отзеркаленные левые)"""
        left_sprites = self._create_left_sprites()
        sprites = []
        
        for sprite in left_sprites:
            # Отзеркаливаем по горизонтали
            flipped = pygame.transform.flip(sprite, True, False)
            sprites.append(flipped)
        
        return sprites
    
    def _draw_player_body(
        self, 
        surface: pygame.Surface, 
        color: Tuple[int, int, int],
        facing_up: bool = False,
        facing_left: bool = False,
        leg_offset: int = 0
    ) -> None:
        """
        Нарисовать тело игрока (пиксельный стиль)
        
        Args:
            surface: Поверхность для рисования
            color: Цвет игрока
            facing_up: Смотрит вверх
            facing_left: Смотрит влево
            leg_offset: Смещение ног для анимации
        """
        center_x = self.tile_size // 2
        center_y = self.tile_size // 2
        
        # Голова (круг)
        head_color = (255, 220, 177)  # Цвет кожи
        pygame.draw.circle(surface, head_color, (center_x, center_y - 6), 5)
        
        # Тело (прямоугольник)
        body_rect = pygame.Rect(center_x - 5, center_y - 2, 10, 12)
        pygame.draw.rect(surface, color, body_rect)
        
        # Руки
        arm_color = color
        if facing_up:
            # Руки по бокам (вид сзади)
            pygame.draw.rect(surface, arm_color, (center_x - 8, center_y, 3, 8))
            pygame.draw.rect(surface, arm_color, (center_x + 5, center_y, 3, 8))
        elif facing_left:
            # Одна рука видна
            pygame.draw.rect(surface, arm_color, (center_x + 3, center_y, 3, 8))
        else:
            # Руки по бокам (вид спереди)
            pygame.draw.rect(surface, arm_color, (center_x - 8, center_y, 3, 8))
            pygame.draw.rect(surface, arm_color, (center_x + 5, center_y, 3, 8))
        
        # Ноги
        leg_color = (50, 50, 100)  # Тёмно-синий
        if facing_up:
            # Ноги (вид сзади)
            pygame.draw.rect(surface, leg_color, (center_x - 5 + leg_offset, center_y + 10, 4, 6))
            pygame.draw.rect(surface, leg_color, (center_x + 1 - leg_offset, center_y + 10, 4, 6))
        elif facing_left:
            # Ноги (вид сбоку)
            pygame.draw.rect(surface, leg_color, (center_x - 2, center_y + 10 + leg_offset, 4, 6))
        else:
            # Ноги (вид спереди)
            pygame.draw.rect(surface, leg_color, (center_x - 5 + leg_offset, center_y + 10, 4, 6))
            pygame.draw.rect(surface, leg_color, (center_x + 1 - leg_offset, center_y + 10, 4, 6))
        
        # Глаза (если не смотрит вверх)
        if not facing_up:
            eye_color = (0, 0, 0)
            if facing_left:
                pygame.draw.circle(surface, eye_color, (center_x - 2, center_y - 7), 1)
            else:
                pygame.draw.circle(surface, eye_color, (center_x - 2, center_y - 7), 1)
                pygame.draw.circle(surface, eye_color, (center_x + 2, center_y - 7), 1)
    
    def update(self, dt: float, is_moving: bool, dx: int, dy: int) -> None:
        """
        Обновить анимацию
        
        Args:
            dt: Delta time
            is_moving: Двигается ли игрок
            dx: Направление по X (-1, 0, 1)
            dy: Направление по Y (-1, 0, 1)
        """
        self.is_moving = is_moving
        
        # Определяем направление
        if is_moving:
            if dy > 0:
                self.current_direction = "down"
            elif dy < 0:
                self.current_direction = "up"
            elif dx < 0:
                self.current_direction = "left"
            elif dx > 0:
                self.current_direction = "right"
        
        # Обновляем анимацию только если двигаемся
        if is_moving:
            self.animation_timer += dt
            
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.animation_frame = (self.animation_frame + 1) % 3
        else:
            # Сбрасываем на первый кадр (стоя)
            self.animation_frame = 0
            self.animation_timer = 0.0
    
    def render(self, screen: pygame.Surface, x: int, y: int) -> None:
        """
        Отрисовать игрока
        
        Args:
            screen: Экран для отрисовки
            x: Позиция X на экране
            y: Позиция Y на экране
        """
        # Получаем текущий спрайт
        sprites = self.sprites[self.current_direction]
        current_sprite = sprites[self.animation_frame]
        
        # Рисуем спрайт
        screen.blit(current_sprite, (x, y))
