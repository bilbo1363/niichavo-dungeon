"""
Класс игрока
"""
import pygame
from dataclasses import dataclass
from ..items.inventory import Inventory
from ..items.item import ItemDatabase
from ..graphics.player_animation import PlayerAnimation


@dataclass
class PlayerStats:
    """Характеристики игрока"""
    health: int = 100
    max_health: int = 100
    endurance: int = 100
    max_endurance: int = 100
    thirst: int = 100
    clarity: int = 100  # Для магии


class Player:
    """Класс игрока"""
    
    def __init__(self, x: int, y: int):
        """
        Инициализация игрока
        
        Args:
            x: Начальная позиция X (в клетках)
            y: Начальная позиция Y (в клетках)
        """
        # Позиция на сетке
        self.x = x
        self.y = y
        
        # Характеристики
        self.stats = PlayerStats()
        
        # Инвентарь
        self.inventory = Inventory(max_slots=20)
        
        # База данных предметов
        self.item_db = ItemDatabase()
        
        # Рюкзак (для совместимости с сохранениями)
        self.backpack = []
        
        # Счётчик шагов
        self.steps = 0
        
        # Лог сообщений (будет установлен из Game)
        self.message_log = None
        
        # Даём стартовые предметы
        self._give_starting_items()
        
        # Визуальные параметры
        self.color = (0, 255, 0)  # Зеленый (для совместимости)
        self.size = 32  # Размер спрайта
        
        # Анимация
        self.animation = PlayerAnimation(tile_size=32)
        self.last_dx = 0
        self.last_dy = 0
        
        print(f"👤 Игрок создан на позиции ({x}, {y})")
        
    def _give_starting_items(self):
        """Выдать стартовые предметы"""
        # Стартовое оружие
        self.inventory.add_item(self.item_db.get_item("rusty_pipe"))
        
        # Стартовые расходники
        self.inventory.add_item(self.item_db.get_item("bandage"), 3)
        self.inventory.add_item(self.item_db.get_item("energy_drink"), 2)
        
        print("📦 Получены стартовые предметы")
        
    def move(self, dx: int, dy: int, level=None) -> bool:
        """
        Перемещение игрока
        
        Args:
            dx: Смещение по X
            dy: Смещение по Y
            level: Уровень для проверки коллизий
            
        Returns:
            True если перемещение успешно
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Если есть уровень - проверяем коллизии
        if level:
            if not level.is_walkable(new_x, new_y):
                return False
        
        # Перемещаемся
        self.x = new_x
        self.y = new_y
        self.steps += 1
        
        # Сохраняем направление для анимации
        self.last_dx = dx
        self.last_dy = dy
        
        # Обновляем статы каждые несколько шагов
        if self.steps % 5 == 0:
            self.update_stats()
            
        return True
        
    def update_stats(self) -> None:
        """Обновление характеристик при ходьбе"""
        # Уменьшаем выносливость
        self.stats.endurance = max(0, self.stats.endurance - 1)
        
        # Если выносливость на нуле - теряем здоровье быстрее
        if self.stats.endurance == 0:
            # При нулевой выносливости теряем здоровье каждые 10 шагов
            if self.steps % 10 == 0:
                self.stats.health = max(0, self.stats.health - 2)
                if self.steps % 20 == 0:  # Сообщение не каждый раз
                    print("⚠️ Вы истощены! Выносливость на нуле!")
                    if self.message_log:
                        self.message_log.warning("⚠️ Вы истощены! Выносливость на нуле!")
        else:
            # Обычная потеря здоровья каждые 25 шагов
            if self.steps % 25 == 0:
                self.stats.health = max(0, self.stats.health - 1)
            
    def take_damage(self, amount: int) -> None:
        """
        Получение урона
        
        Args:
            amount: Количество урона
        """
        self.stats.health = max(0, self.stats.health - amount)
        if self.stats.health == 0:
            print("💀 Игрок погиб!")
            
    def heal(self, amount: int) -> None:
        """
        Лечение
        
        Args:
            amount: Количество восстановленного здоровья
        """
        self.stats.health = min(
            self.stats.max_health,
            self.stats.health + amount
        )
        
    def update(self, dt: float, is_moving: bool = False) -> None:
        """
        Обновление игрока
        
        Args:
            dt: Delta time
            is_moving: Двигается ли игрок в данный момент
        """
        # Обновляем анимацию
        self.animation.update(dt, is_moving, self.last_dx, self.last_dy)
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
        """
        Отрисовка игрока
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
        """
        # Вычисляем позицию на экране
        screen_x = self.x * self.size - camera_x
        screen_y = self.y * self.size - camera_y
        
        # Рисуем анимированного игрока
        self.animation.render(screen, screen_x, screen_y)


if __name__ == "__main__":
    # Тест класса Player
    player = Player(10, 10)
    print(f"Позиция: ({player.x}, {player.y})")
    print(f"Здоровье: {player.stats.health}/{player.stats.max_health}")
    
    # Тест движения
    player.move(1, 0)
    print(f"После движения: ({player.x}, {player.y})")
    print(f"Шагов: {player.steps}")
