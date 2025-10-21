"""
Система способностей и умений
Версия: 0.4.0
Этап 0, Неделя 2
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum
from .modifiers import StatModifier, ModifierType, ModifierSource


class AbilityType(Enum):
    """Тип способности"""
    PASSIVE = "passive"    # Пассивная (всегда активна)
    ACTIVE = "active"      # Активная (требует активации)
    TOGGLE = "toggle"      # Переключаемая (вкл/выкл)


class AbilityCategory(Enum):
    """Категория способности"""
    COMBAT = "combat"              # Боевые
    SURVIVAL = "survival"          # Выживание
    EXPLORATION = "exploration"    # Исследование
    CRAFTING = "crafting"          # Крафт
    MAGIC = "magic"                # Магия


@dataclass
class AbilityRequirement:
    """Требование для разблокировки способности"""
    
    required_level: int = 1                    # Минимальный уровень
    required_abilities: List[str] = None       # ID требуемых способностей
    required_stats: Dict[str, int] = None      # Минимальные характеристики
    
    def __post_init__(self):
        if self.required_abilities is None:
            self.required_abilities = []
        if self.required_stats is None:
            self.required_stats = {}
    
    def is_met(self, level: int, unlocked_abilities: Set[str], 
               stats: Dict[str, int]) -> bool:
        """
        Проверить, выполнены ли требования
        
        Args:
            level: Уровень игрока
            unlocked_abilities: Множество разблокированных способностей
            stats: Характеристики игрока
            
        Returns:
            True если все требования выполнены
        """
        # Проверка уровня
        if level < self.required_level:
            return False
        
        # Проверка требуемых способностей
        for ability_id in self.required_abilities:
            if ability_id not in unlocked_abilities:
                return False
        
        # Проверка характеристик
        for stat_name, min_value in self.required_stats.items():
            if stats.get(stat_name, 0) < min_value:
                return False
        
        return True


@dataclass
class Ability:
    """Способность игрока"""
    
    id: str                                    # Уникальный ID
    name: str                                  # Название
    description: str                           # Описание
    ability_type: AbilityType                  # Тип способности
    category: AbilityCategory                  # Категория
    
    # Требования
    requirements: AbilityRequirement           # Требования для разблокировки
    cost: int = 1                              # Стоимость в очках способностей
    
    # Эффекты (для пассивных способностей)
    stat_modifiers: List[StatModifier] = None  # Модификаторы характеристик
    
    # Для активных способностей
    cooldown: int = 0                          # Перезарядка в ходах
    stamina_cost: int = 0                      # Стоимость выносливости
    
    # Визуал
    icon: str = ""                             # Путь к иконке
    tier: int = 1                              # Уровень в дереве (1-5)
    
    def __post_init__(self):
        if self.stat_modifiers is None:
            self.stat_modifiers = []
    
    def can_unlock(self, level: int, unlocked_abilities: Set[str],
                   stats: Dict[str, int], available_points: int) -> bool:
        """
        Проверить, можно ли разблокировать способность
        
        Args:
            level: Уровень игрока
            unlocked_abilities: Разблокированные способности
            stats: Характеристики игрока
            available_points: Доступные очки способностей
            
        Returns:
            True если можно разблокировать
        """
        # Проверка очков
        if available_points < self.cost:
            return False
        
        # Проверка требований
        return self.requirements.is_met(level, unlocked_abilities, stats)
    
    def to_dict(self) -> dict:
        """Сериализация"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ability_type': self.ability_type.value,
            'category': self.category.value,
            'cost': self.cost,
            'tier': self.tier
        }


class AbilityTree:
    """Дерево способностей"""
    
    def __init__(self):
        self.abilities: Dict[str, Ability] = {}           # Все способности
        self.unlocked: Set[str] = set()                   # Разблокированные
        self.active_toggles: Set[str] = set()             # Активные переключаемые
        self.cooldowns: Dict[str, int] = {}               # Текущие перезарядки
    
    def register_ability(self, ability: Ability):
        """
        Зарегистрировать способность в дереве
        
        Args:
            ability: Способность для регистрации
        """
        self.abilities[ability.id] = ability
    
    def can_unlock(self, ability_id: str, level: int, stats: Dict[str, int],
                   available_points: int) -> bool:
        """
        Проверить, можно ли разблокировать способность
        
        Args:
            ability_id: ID способности
            level: Уровень игрока
            stats: Характеристики игрока
            available_points: Доступные очки способностей
            
        Returns:
            True если можно разблокировать
        """
        if ability_id not in self.abilities:
            return False
        
        # Уже разблокирована
        if ability_id in self.unlocked:
            return False
        
        ability = self.abilities[ability_id]
        return ability.can_unlock(level, self.unlocked, stats, available_points)
    
    def unlock(self, ability_id: str) -> bool:
        """
        Разблокировать способность
        
        Args:
            ability_id: ID способности
            
        Returns:
            True если разблокировка успешна
        """
        if ability_id not in self.abilities:
            return False
        
        if ability_id in self.unlocked:
            return False
        
        self.unlocked.add(ability_id)
        return True
    
    def is_unlocked(self, ability_id: str) -> bool:
        """Проверить, разблокирована ли способность"""
        return ability_id in self.unlocked
    
    def get_ability(self, ability_id: str) -> Optional[Ability]:
        """Получить способность по ID"""
        return self.abilities.get(ability_id)
    
    def get_unlocked_abilities(self) -> List[Ability]:
        """Получить список разблокированных способностей"""
        return [self.abilities[aid] for aid in self.unlocked if aid in self.abilities]
    
    def get_available_abilities(self, level: int, stats: Dict[str, int],
                                available_points: int) -> List[Ability]:
        """
        Получить список доступных для разблокировки способностей
        
        Args:
            level: Уровень игрока
            stats: Характеристики игрока
            available_points: Доступные очки способностей
            
        Returns:
            Список доступных способностей
        """
        available = []
        for ability_id, ability in self.abilities.items():
            if self.can_unlock(ability_id, level, stats, available_points):
                available.append(ability)
        return available
    
    def get_abilities_by_category(self, category: AbilityCategory) -> List[Ability]:
        """Получить все способности категории"""
        return [a for a in self.abilities.values() if a.category == category]
    
    def get_abilities_by_tier(self, tier: int) -> List[Ability]:
        """Получить все способности уровня"""
        return [a for a in self.abilities.values() if a.tier == tier]
    
    def toggle_ability(self, ability_id: str) -> bool:
        """
        Переключить активную способность
        
        Args:
            ability_id: ID способности
            
        Returns:
            True если способность теперь активна
        """
        if ability_id not in self.unlocked:
            return False
        
        ability = self.abilities.get(ability_id)
        if not ability or ability.ability_type != AbilityType.TOGGLE:
            return False
        
        if ability_id in self.active_toggles:
            self.active_toggles.remove(ability_id)
            return False
        else:
            self.active_toggles.add(ability_id)
            return True
    
    def is_active(self, ability_id: str) -> bool:
        """Проверить, активна ли переключаемая способность"""
        return ability_id in self.active_toggles
    
    def use_ability(self, ability_id: str) -> bool:
        """
        Использовать активную способность
        
        Args:
            ability_id: ID способности
            
        Returns:
            True если использование успешно
        """
        if ability_id not in self.unlocked:
            return False
        
        ability = self.abilities.get(ability_id)
        if not ability or ability.ability_type != AbilityType.ACTIVE:
            return False
        
        # Проверка перезарядки
        if ability_id in self.cooldowns and self.cooldowns[ability_id] > 0:
            return False
        
        # Установить перезарядку
        if ability.cooldown > 0:
            self.cooldowns[ability_id] = ability.cooldown
        
        return True
    
    def update_cooldowns(self):
        """Обновить перезарядки (вызывать каждый ход)"""
        for ability_id in list(self.cooldowns.keys()):
            self.cooldowns[ability_id] -= 1
            if self.cooldowns[ability_id] <= 0:
                del self.cooldowns[ability_id]
    
    def get_cooldown(self, ability_id: str) -> int:
        """Получить текущую перезарядку способности"""
        return self.cooldowns.get(ability_id, 0)
    
    def get_all_stat_modifiers(self) -> List[StatModifier]:
        """Получить все модификаторы от разблокированных пассивных способностей"""
        modifiers = []
        for ability_id in self.unlocked:
            ability = self.abilities.get(ability_id)
            if ability and ability.ability_type == AbilityType.PASSIVE:
                modifiers.extend(ability.stat_modifiers)
            elif ability and ability.ability_type == AbilityType.TOGGLE:
                if ability_id in self.active_toggles:
                    modifiers.extend(ability.stat_modifiers)
        return modifiers
    
    def to_dict(self) -> dict:
        """Сериализация"""
        return {
            'unlocked': list(self.unlocked),
            'active_toggles': list(self.active_toggles),
            'cooldowns': self.cooldowns
        }
    
    @classmethod
    def from_dict(cls, data: dict, abilities: Dict[str, Ability]) -> 'AbilityTree':
        """Десериализация"""
        tree = cls()
        tree.abilities = abilities
        tree.unlocked = set(data.get('unlocked', []))
        tree.active_toggles = set(data.get('active_toggles', []))
        tree.cooldowns = data.get('cooldowns', {})
        return tree
