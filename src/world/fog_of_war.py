"""
Система тумана войны (Fog of War)
"""
import numpy as np
from typing import Set, Tuple


class FogOfWar:
    """Система тумана войны"""
    
    # Состояния видимости
    UNEXPLORED = 0  # Не исследовано (черный)
    EXPLORED = 1    # Исследовано ранее (серый)
    VISIBLE = 2     # Видимо сейчас (полный цвет)
    
    def __init__(self, width: int, height: int):
        """
        Инициализация тумана войны
        
        Args:
            width: Ширина карты
            height: Высота карты
        """
        self.width = width
        self.height = height
        
        # Карта видимости (0 = не исследовано, 1 = исследовано, 2 = видимо)
        self.visibility = np.zeros((height, width), dtype=np.uint8)
        
        # Радиус обзора игрока
        self.vision_radius = 5
        
        print(f"🌫️  Fog of War создан ({width}x{height})")
        
    def update_vision(self, player_x: int, player_y: int, level_tiles: np.ndarray) -> None:
        """
        Обновить видимость вокруг игрока
        
        Args:
            player_x: Позиция игрока X
            player_y: Позиция игрока Y
            level_tiles: Тайлы уровня для проверки стен
        """
        # Сбрасываем текущую видимость (VISIBLE → EXPLORED)
        self.visibility[self.visibility == self.VISIBLE] = self.EXPLORED
        
        # Вычисляем видимую область (простой круг)
        for dy in range(-self.vision_radius, self.vision_radius + 1):
            for dx in range(-self.vision_radius, self.vision_radius + 1):
                # Проверяем расстояние (круг)
                distance = (dx * dx + dy * dy) ** 0.5
                if distance > self.vision_radius:
                    continue
                    
                x = player_x + dx
                y = player_y + dy
                
                # Проверяем границы
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue
                    
                # Проверяем line of sight (упрощенно - без ray casting пока)
                if self._has_line_of_sight(player_x, player_y, x, y, level_tiles):
                    self.visibility[y, x] = self.VISIBLE
                    
    def _has_line_of_sight(
        self, 
        x0: int, 
        y0: int, 
        x1: int, 
        y1: int, 
        level_tiles: np.ndarray
    ) -> bool:
        """
        Проверка прямой видимости (упрощенная)
        
        Args:
            x0, y0: Начальная точка
            x1, y1: Конечная точка
            level_tiles: Тайлы уровня
            
        Returns:
            True если есть прямая видимость
        """
        # Упрощенная проверка - просто проверяем конечную точку
        # TODO: Добавить полноценный ray casting позже
        if 0 <= x1 < self.width and 0 <= y1 < self.height:
            # Если конечная точка - стена, всё равно показываем её
            return True
        return False
        
    def is_visible(self, x: int, y: int) -> bool:
        """
        Проверить, видима ли клетка сейчас
        
        Args:
            x, y: Координаты
            
        Returns:
            True если видима
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.visibility[y, x] == self.VISIBLE
        
    def is_explored(self, x: int, y: int) -> bool:
        """
        Проверить, исследована ли клетка
        
        Args:
            x, y: Координаты
            
        Returns:
            True если исследована (хотя бы раз была видна)
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.visibility[y, x] >= self.EXPLORED
        
    def get_visibility(self, x: int, y: int) -> int:
        """
        Получить уровень видимости клетки
        
        Args:
            x, y: Координаты
            
        Returns:
            Уровень видимости (0, 1, или 2)
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return self.UNEXPLORED
        return self.visibility[y, x]
        
    def reveal_all(self) -> None:
        """Открыть всю карту (для отладки)"""
        self.visibility.fill(self.VISIBLE)
        
    def reset(self) -> None:
        """Сбросить всю видимость"""
        self.visibility.fill(self.UNEXPLORED)


if __name__ == "__main__":
    # Тест FogOfWar
    fog = FogOfWar(60, 40)
    print(f"Размер: {fog.width}x{fog.height}")
    print(f"Радиус обзора: {fog.vision_radius}")
    
    # Тестовые тайлы
    test_tiles = np.zeros((40, 60), dtype=np.uint8)
    
    # Обновляем видимость
    fog.update_vision(30, 20, test_tiles)
    
    print(f"Клетка (30, 20) видима: {fog.is_visible(30, 20)}")
    print(f"Клетка (0, 0) видима: {fog.is_visible(0, 0)}")
