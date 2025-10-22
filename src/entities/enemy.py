"""
Система врагов
"""
import pygame
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class EnemyType(Enum):
    """Типы врагов"""
    RAT = "rat"                 # Крыса (слабый)
    ZOMBIE = "zombie"           # Зомби (средний)
    GHOST = "ghost"             # Призрак (сильный)
    MUTANT = "mutant"           # Мутант (очень сильный)


@dataclass
class EnemyStats:
    """Характеристики врага"""
    health: int = 30
    max_health: int = 30
    damage: int = 5
    speed: float = 0.5          # Скорость движения (клеток в секунду)
    detection_range: int = 8    # Дальность обнаружения игрока
    attack_range: int = 1       # Дальность атаки


class Enemy:
    """Класс врага"""
    
    def __init__(self, enemy_type: EnemyType, x: int, y: int):
        """
        Инициализация врага
        
        Args:
            enemy_type: Тип врага
            x: Позиция X
            y: Позиция Y
        """
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        
        # Характеристики
        self.stats = self._get_stats_for_type(enemy_type)
        
        # AI состояние
        self.state = "idle"  # idle, patrol, chase, attack
        self.target_x: Optional[int] = None
        self.target_y: Optional[int] = None
        
        # Патрулирование
        self.patrol_points = []
        self.current_patrol_index = 0
        
        # Таймеры
        self.move_cooldown = 0.0
        self.attack_cooldown = 0.0
        self.attack_delay = 1.0  # Секунд между атаками
        
        # Визуальные параметры
        self.color = self._get_color_for_type(enemy_type)
        self.size = 32
        
        # Флаги
        self.is_dead = False
        self.aggro = False  # Агрессивен ли враг
        
    def _get_stats_for_type(self, enemy_type: EnemyType) -> EnemyStats:
        """
        Получить характеристики для типа врага
        
        Args:
            enemy_type: Тип врага
            
        Returns:
            Характеристики
        """
        stats_map = {
            EnemyType.RAT: EnemyStats(
                health=20, max_health=20, damage=3, speed=1.0, 
                detection_range=6, attack_range=1
            ),
            EnemyType.ZOMBIE: EnemyStats(
                health=50, max_health=50, damage=8, speed=0.5, 
                detection_range=10, attack_range=1
            ),
            EnemyType.GHOST: EnemyStats(
                health=30, max_health=30, damage=12, speed=0.8, 
                detection_range=12, attack_range=2
            ),
            EnemyType.MUTANT: EnemyStats(
                health=80, max_health=80, damage=15, speed=0.6, 
                detection_range=15, attack_range=1
            ),
        }
        return stats_map.get(enemy_type, EnemyStats())
    
    def get_xp_reward(self) -> int:
        """
        Получить награду опыта за убийство врага
        
        Returns:
            Количество опыта
        """
        xp_map = {
            EnemyType.RAT: 10,      # Слабый враг
            EnemyType.ZOMBIE: 20,   # Средний враг
            EnemyType.GHOST: 35,    # Сильный враг
            EnemyType.MUTANT: 50,   # Очень сильный враг
        }
        return xp_map.get(self.enemy_type, 5)
        
    def _get_color_for_type(self, enemy_type: EnemyType) -> Tuple[int, int, int]:
        """
        Получить цвет для типа врага
        
        Args:
            enemy_type: Тип врага
            
        Returns:
            RGB цвет
        """
        color_map = {
            EnemyType.RAT: (139, 69, 19),      # Коричневый
            EnemyType.ZOMBIE: (100, 150, 100), # Зелёный
            EnemyType.GHOST: (200, 200, 255),  # Голубой
            EnemyType.MUTANT: (200, 50, 50),   # Красный
        }
        return color_map.get(enemy_type, (255, 0, 255))
        
    def update(self, dt: float, player_x: int, player_y: int, level) -> Optional[str]:
        """
        Обновление врага
        
        Args:
            dt: Delta time
            player_x: Позиция игрока X
            player_y: Позиция игрока Y
            level: Уровень
            
        Returns:
            Действие ("attack" если атакует)
        """
        if self.is_dead:
            return None
            
        # Обновляем таймеры
        self.move_cooldown = max(0, self.move_cooldown - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        
        # Проверяем дистанцию до игрока
        distance = abs(self.x - player_x) + abs(self.y - player_y)
        
        # AI логика
        if distance <= self.stats.attack_range:
            # Атака
            self.state = "attack"
            if self.attack_cooldown <= 0:
                self.attack_cooldown = self.attack_delay
                return "attack"
                
        elif distance <= self.stats.detection_range:
            # Преследование
            self.state = "chase"
            self.aggro = True
            self.target_x = player_x
            self.target_y = player_y
            
            # Двигаемся к игроку
            if self.move_cooldown <= 0:
                self._move_towards_target(level)
                self.move_cooldown = 1.0 / self.stats.speed
                
        elif self.aggro:
            # Продолжаем преследование если агрессивны
            self.state = "chase"
            if self.move_cooldown <= 0:
                self._move_towards_target(level)
                self.move_cooldown = 1.0 / self.stats.speed
                
        else:
            # Патрулирование или простой
            self.state = "patrol"
            if self.move_cooldown <= 0 and random.random() < 0.3:
                self._patrol_move(level)
                self.move_cooldown = 1.0 / self.stats.speed
                
        return None
        
    def _move_towards_target(self, level) -> bool:
        """
        Двигаться к цели
        
        Args:
            level: Уровень
            
        Returns:
            True если сдвинулся
        """
        if self.target_x is None or self.target_y is None:
            return False
            
        # Простой AI - двигаемся по одной оси за раз
        dx = 0
        dy = 0
        
        if self.x < self.target_x:
            dx = 1
        elif self.x > self.target_x:
            dx = -1
        elif self.y < self.target_y:
            dy = 1
        elif self.y > self.target_y:
            dy = -1
            
        # Проверяем коллизию
        new_x = self.x + dx
        new_y = self.y + dy
        
        if level.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
            
        # Если не можем двигаться прямо, пробуем другую ось
        if dx != 0:
            if self.y < self.target_y and level.is_walkable(self.x, self.y + 1):
                self.y += 1
                return True
            elif self.y > self.target_y and level.is_walkable(self.x, self.y - 1):
                self.y -= 1
                return True
        elif dy != 0:
            if self.x < self.target_x and level.is_walkable(self.x + 1, self.y):
                self.x += 1
                return True
            elif self.x > self.target_x and level.is_walkable(self.x - 1, self.y):
                self.x -= 1
                return True
                
        return False
        
    def _patrol_move(self, level) -> bool:
        """
        Случайное патрулирование
        
        Args:
            level: Уровень
            
        Returns:
            True если сдвинулся
        """
        # Случайное направление
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            
            if level.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y
                return True
                
        return False
        
    def take_damage(self, damage: int) -> bool:
        """
        Получить урон
        
        Args:
            damage: Количество урона
            
        Returns:
            True если враг умер
        """
        self.stats.health -= damage
        self.aggro = True  # Становится агрессивным
        
        if self.stats.health <= 0:
            self.stats.health = 0
            self.is_dead = True
            print(f"💀 {self.enemy_type.value.capitalize()} убит!")
            return True
            
        return False
        
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, fog_of_war=None) -> None:
        """
        Отрисовка врага
        
        Args:
            screen: Поверхность для отрисовки
            camera_x: Смещение камеры по X
            camera_y: Смещение камеры по Y
            fog_of_war: Туман войны
        """
        if self.is_dead:
            return
            
        # Проверяем видимость
        if fog_of_war and not fog_of_war.is_visible(self.x, self.y):
            return
            
        # Вычисляем позицию на экране
        screen_x = self.x * self.size - camera_x
        screen_y = self.y * self.size - camera_y
        
        # Рисуем врага
        pygame.draw.circle(
            screen,
            self.color,
            (screen_x + self.size // 2, screen_y + self.size // 2),
            self.size // 3
        )
        
        # Контур
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (screen_x + self.size // 2, screen_y + self.size // 2),
            self.size // 3,
            1
        )
        
        # Полоска здоровья
        if self.stats.health < self.stats.max_health:
            bar_width = self.size
            bar_height = 4
            bar_x = screen_x
            bar_y = screen_y - 8
            
            # Фон
            pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # Здоровье
            health_width = int(bar_width * (self.stats.health / self.stats.max_health))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))


if __name__ == "__main__":
    # Тест врага
    enemy = Enemy(EnemyType.ZOMBIE, 10, 10)
    print(f"Враг: {enemy.enemy_type.value}")
    print(f"Здоровье: {enemy.stats.health}/{enemy.stats.max_health}")
    print(f"Урон: {enemy.stats.damage}")
    print(f"Скорость: {enemy.stats.speed}")
    
    # Тест урона
    enemy.take_damage(20)
    print(f"После урона: {enemy.stats.health}/{enemy.stats.max_health}")
