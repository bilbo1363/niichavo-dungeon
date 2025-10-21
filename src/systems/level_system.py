"""
Система уровней и опыта
Версия: 0.4.0
Этап 0, Неделя 1
"""

from typing import Callable, Optional
import math


class LevelSystem:
    """Система прогрессии игрока через уровни и опыт"""
    
    def __init__(self, level: int = 1, experience: int = 0):
        self.level = level
        self.experience = experience
        self.exp_to_next_level = self.calculate_exp_for_level(level + 1)
        
        # Очки способностей (ability points)
        self.ability_points = 0
        
        # Коллбэк для уведомления о повышении уровня
        self.on_level_up: Optional[Callable[[int], None]] = None
    
    @staticmethod
    def calculate_exp_for_level(level: int) -> int:
        """
        Рассчитать необходимый опыт для достижения уровня
        
        Формула: 100 * level^1.5
        
        Args:
            level: Целевой уровень
            
        Returns:
            Необходимое количество опыта
        """
        if level <= 1:
            return 0
        
        return int(100 * math.pow(level, 1.5))
    
    def gain_exp(self, amount: int) -> list[int]:
        """
        Получить опыт
        
        Args:
            amount: Количество опыта
            
        Returns:
            Список уровней, которые были получены (может быть пустым или содержать несколько уровней)
        """
        if amount <= 0:
            return []
        
        self.experience += amount
        levels_gained = []
        
        # Проверка повышения уровня (может быть несколько уровней за раз)
        while self.experience >= self.exp_to_next_level:
            self.level_up()
            levels_gained.append(self.level)
        
        return levels_gained
    
    def level_up(self):
        """Повышение уровня"""
        # Вычесть опыт для текущего уровня
        self.experience -= self.exp_to_next_level
        
        # Повысить уровень
        self.level += 1
        
        # Рассчитать опыт для следующего уровня
        self.exp_to_next_level = self.calculate_exp_for_level(self.level + 1)
        
        # Дать очко способностей
        self.ability_points += 1
        
        # Вызвать коллбэк если установлен
        if self.on_level_up:
            self.on_level_up(self.level)
    
    def get_level_progress(self) -> float:
        """
        Получить прогресс до следующего уровня
        
        Returns:
            Прогресс от 0.0 до 1.0
        """
        if self.exp_to_next_level == 0:
            return 1.0
        
        return min(1.0, self.experience / self.exp_to_next_level)
    
    def get_level_progress_percent(self) -> int:
        """
        Получить прогресс до следующего уровня в процентах
        
        Returns:
            Прогресс от 0 до 100
        """
        return int(self.get_level_progress() * 100)
    
    def spend_ability_point(self) -> bool:
        """
        Потратить очко способностей
        
        Returns:
            True если очко было потрачено, False если очков нет
        """
        if self.ability_points > 0:
            self.ability_points -= 1
            return True
        return False
    
    def can_spend_ability_point(self) -> bool:
        """Проверка, есть ли доступные очки способностей"""
        return self.ability_points > 0
    
    def to_dict(self) -> dict:
        """Сериализация для сохранения"""
        return {
            'level': self.level,
            'experience': self.experience,
            'ability_points': self.ability_points
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LevelSystem':
        """Десериализация из сохранения"""
        level_system = cls(
            level=data.get('level', 1),
            experience=data.get('experience', 0)
        )
        level_system.ability_points = data.get('ability_points', 0)
        return level_system


class ExperienceRewards:
    """Награды опытом за различные действия"""
    
    # Враги
    ENEMY_KILL_BASE = 10
    ENEMY_KILL_MULTIPLIER = 1.5  # Множитель за уровень врага
    
    # Исследование
    DISCOVER_ROOM = 5
    DISCOVER_SECRET = 20
    FIND_ARTIFACT = 15
    READ_NOTE = 3
    
    # Крафт
    CRAFT_ITEM = 5
    CRAFT_RARE_ITEM = 15
    UPGRADE_STATION = 25
    
    # Прогрессия
    COMPLETE_FLOOR = 50
    SURVIVE_WITHOUT_DEATH = 25
    
    # Исследование врагов (Журнал исследователя)
    OBSERVE_ENEMY_FIRST_TIME = 5
    LEARN_ENEMY_WEAKNESS = 10
    MASTER_ENEMY = 20
    
    # Ловушки
    AVOID_TRAP = 2
    DISARM_TRAP = 5
    
    @staticmethod
    def calculate_enemy_exp(enemy_level: int) -> int:
        """
        Рассчитать опыт за убийство врага
        
        Args:
            enemy_level: Уровень врага
            
        Returns:
            Количество опыта
        """
        return int(ExperienceRewards.ENEMY_KILL_BASE * 
                  math.pow(ExperienceRewards.ENEMY_KILL_MULTIPLIER, enemy_level - 1))
    
    @staticmethod
    def calculate_floor_completion_exp(floor_number: int) -> int:
        """
        Рассчитать опыт за прохождение этажа
        
        Args:
            floor_number: Номер этажа
            
        Returns:
            Количество опыта
        """
        return ExperienceRewards.COMPLETE_FLOOR + (floor_number * 10)


# Таблица уровней для справки
LEVEL_TABLE = {
    1: 0,
    2: 141,      # 100 * 2^1.5
    3: 519,      # 100 * 3^1.5
    4: 1131,     # 100 * 4^1.5
    5: 1976,     # 100 * 5^1.5
    10: 10000,   # 100 * 10^1.5
    15: 29240,   # 100 * 15^1.5
    20: 56568,   # 100 * 20^1.5
}
