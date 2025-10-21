"""
Система характеристик игрока
Версия: 0.4.0
Этап 0, Неделя 1
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PlayerStats:
    """Базовые характеристики игрока"""
    
    # Основные характеристики
    health: int = 100
    max_health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    
    # Боевые характеристики
    attack: int = 10          # Базовый урон
    defense: int = 5          # Защита
    accuracy: float = 0.8     # Точность (0.0-1.0)
    evasion: float = 0.1      # Уклонение (0.0-1.0)
    critical_chance: float = 0.05  # Шанс критического удара
    critical_damage: float = 1.5   # Множитель критического урона
    
    # Исследовательские характеристики
    perception: int = 5       # Восприятие (обнаружение ловушек, секретов)
    intelligence: int = 5     # Интеллект (крафт, изучение, магия)
    luck: int = 5            # Удача (лут, случайные события)
    
    # Скорость и движение
    movement_speed: float = 1.0  # Множитель скорости движения
    
    def __post_init__(self):
        """Валидация характеристик"""
        # Здоровье не может быть больше максимума
        self.health = min(self.health, self.max_health)
        self.stamina = min(self.stamina, self.max_stamina)
        
        # Ограничения для процентных значений
        self.accuracy = max(0.0, min(1.0, self.accuracy))
        self.evasion = max(0.0, min(0.75, self.evasion))  # Максимум 75% уклонения
        self.critical_chance = max(0.0, min(0.5, self.critical_chance))  # Максимум 50% крита
    
    def take_damage(self, damage: int) -> int:
        """
        Получить урон
        
        Args:
            damage: Количество урона
            
        Returns:
            Фактический полученный урон
        """
        # Применить защиту (каждая единица защиты снижает урон на 1)
        actual_damage = max(1, damage - self.defense)
        
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Восстановить здоровье
        
        Args:
            amount: Количество восстановления
            
        Returns:
            Фактически восстановленное здоровье
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health
    
    def restore_stamina(self, amount: int) -> int:
        """
        Восстановить выносливость
        
        Args:
            amount: Количество восстановления
            
        Returns:
            Фактически восстановленная выносливость
        """
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def use_stamina(self, amount: int) -> bool:
        """
        Использовать выносливость
        
        Args:
            amount: Количество выносливости
            
        Returns:
            True если хватило выносливости, False иначе
        """
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
    
    def is_alive(self) -> bool:
        """Проверка, жив ли игрок"""
        return self.health > 0
    
    def get_effective_attack(self) -> int:
        """Получить эффективный урон с учётом всех модификаторов"""
        # Базовый урон (будет расширено модификаторами позже)
        return self.attack
    
    def get_effective_defense(self) -> int:
        """Получить эффективную защиту с учётом всех модификаторов"""
        # Базовая защита (будет расширено модификаторами позже)
        return self.defense
    
    def to_dict(self) -> dict:
        """Сериализация для сохранения"""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'attack': self.attack,
            'defense': self.defense,
            'accuracy': self.accuracy,
            'evasion': self.evasion,
            'critical_chance': self.critical_chance,
            'critical_damage': self.critical_damage,
            'perception': self.perception,
            'intelligence': self.intelligence,
            'luck': self.luck,
            'movement_speed': self.movement_speed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerStats':
        """Десериализация из сохранения"""
        return cls(**data)


# Предустановленные наборы характеристик для разных режимов сложности
DIFFICULTY_PRESETS = {
    'explorer': PlayerStats(
        max_health=150,
        health=150,
        max_stamina=120,
        stamina=120,
        attack=12,
        defense=8,
        perception=7,
        intelligence=7,
        luck=7
    ),
    'scientist': PlayerStats(
        max_health=100,
        health=100,
        max_stamina=100,
        stamina=100,
        attack=10,
        defense=5,
        perception=5,
        intelligence=5,
        luck=5
    ),
    'stalker': PlayerStats(
        max_health=75,
        health=75,
        max_stamina=80,
        stamina=80,
        attack=8,
        defense=3,
        perception=4,
        intelligence=4,
        luck=4
    )
}


def get_stats_for_difficulty(difficulty: str) -> PlayerStats:
    """
    Получить характеристики для выбранного режима сложности
    
    Args:
        difficulty: 'explorer', 'scientist', или 'stalker'
        
    Returns:
        PlayerStats с соответствующими характеристиками
    """
    if difficulty in DIFFICULTY_PRESETS:
        return DIFFICULTY_PRESETS[difficulty]
    
    # По умолчанию - scientist (нормальная сложность)
    return DIFFICULTY_PRESETS['scientist']
