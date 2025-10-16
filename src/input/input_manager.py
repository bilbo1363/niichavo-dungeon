"""
Менеджер ввода
"""
import pygame
from typing import Dict, Set


class InputManager:
    """Менеджер обработки ввода"""
    
    def __init__(self):
        """Инициализация менеджера ввода"""
        # Состояние клавиш
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # Маппинг клавиш для движения
        self.movement_keys = {
            # WASD
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0),
            # Стрелки
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
        }
        
    def update(self, events: list) -> None:
        """
        Обновление состояния ввода
        
        Args:
            events: Список событий Pygame
        """
        # Очищаем "только что нажатые/отпущенные"
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        # Обрабатываем события
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
                
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                self.keys_just_released.add(event.key)
                
    def is_key_pressed(self, key: int) -> bool:
        """
        Проверка, нажата ли клавиша (удерживается)
        
        Args:
            key: Код клавиши (pygame.K_*)
            
        Returns:
            True если клавиша нажата
        """
        return key in self.keys_pressed
        
    def is_key_just_pressed(self, key: int) -> bool:
        """
        Проверка, была ли клавиша только что нажата
        
        Args:
            key: Код клавиши (pygame.K_*)
            
        Returns:
            True если клавиша только что нажата
        """
        return key in self.keys_just_pressed
        
    def get_movement_input(self) -> tuple[int, int]:
        """
        Получить направление движения из ввода
        
        Returns:
            Кортеж (dx, dy) направления движения
        """
        dx, dy = 0, 0
        
        # Проверяем клавиши движения (удерживаемые клавиши)
        for key, (key_dx, key_dy) in self.movement_keys.items():
            if self.is_key_pressed(key):
                dx += key_dx
                dy += key_dy
                break  # Берём только первое направление
                
        return (dx, dy)


if __name__ == "__main__":
    # Тест InputManager
    manager = InputManager()
    print("✅ InputManager создан")
    print(f"Клавиши движения: {len(manager.movement_keys)}")
