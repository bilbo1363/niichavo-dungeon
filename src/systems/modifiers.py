"""
Система модификаторов характеристик
Версия: 0.4.0
Этап 0, Неделя 1
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ModifierType(Enum):
    """Тип модификатора"""
    FLAT = "flat"          # Плоское значение (+10 к атаке)
    PERCENT = "percent"    # Процентное значение (+20% к атаке)
    MULTIPLY = "multiply"  # Множитель (x1.5 к атаке)


class ModifierSource(Enum):
    """Источник модификатора"""
    ABILITY = "ability"              # Способность
    ITEM = "item"                    # Предмет
    BUFF = "buff"                    # Временный бафф
    DEBUFF = "debuff"                # Временный дебафф
    RESEARCH = "research"            # Журнал исследователя
    STATION = "station"              # Крафт-станция
    ENVIRONMENT = "environment"      # Окружение (биом, комната)


@dataclass
class StatModifier:
    """Модификатор характеристики"""
    
    stat_name: str                    # Название характеристики
    value: float                      # Значение модификатора
    modifier_type: ModifierType       # Тип модификатора
    source: ModifierSource            # Источник модификатора
    source_id: str                    # ID источника (например, "ability_tough")
    duration: int = -1                # Длительность в ходах (-1 = постоянный)
    description: str = ""             # Описание модификатора
    
    def is_permanent(self) -> bool:
        """Проверка, постоянный ли модификатор"""
        return self.duration == -1
    
    def is_expired(self) -> bool:
        """Проверка, истёк ли модификатор"""
        return self.duration == 0 and not self.is_permanent()
    
    def tick(self):
        """Уменьшить длительность на 1 ход"""
        if not self.is_permanent():
            self.duration = max(0, self.duration - 1)
    
    def to_dict(self) -> dict:
        """Сериализация"""
        return {
            'stat_name': self.stat_name,
            'value': self.value,
            'modifier_type': self.modifier_type.value,
            'source': self.source.value,
            'source_id': self.source_id,
            'duration': self.duration,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StatModifier':
        """Десериализация"""
        return cls(
            stat_name=data['stat_name'],
            value=data['value'],
            modifier_type=ModifierType(data['modifier_type']),
            source=ModifierSource(data['source']),
            source_id=data['source_id'],
            duration=data.get('duration', -1),
            description=data.get('description', '')
        )


class ModifierManager:
    """Менеджер модификаторов"""
    
    def __init__(self):
        self.modifiers: List[StatModifier] = []
    
    def add_modifier(self, modifier: StatModifier):
        """
        Добавить модификатор
        
        Args:
            modifier: Модификатор для добавления
        """
        self.modifiers.append(modifier)
    
    def remove_modifier(self, source_id: str) -> bool:
        """
        Удалить модификатор по ID источника
        
        Args:
            source_id: ID источника модификатора
            
        Returns:
            True если модификатор был удалён
        """
        initial_count = len(self.modifiers)
        self.modifiers = [m for m in self.modifiers if m.source_id != source_id]
        return len(self.modifiers) < initial_count
    
    def remove_modifiers_by_source(self, source: ModifierSource) -> int:
        """
        Удалить все модификаторы от определённого источника
        
        Args:
            source: Источник модификаторов
            
        Returns:
            Количество удалённых модификаторов
        """
        initial_count = len(self.modifiers)
        self.modifiers = [m for m in self.modifiers if m.source != source]
        return initial_count - len(self.modifiers)
    
    def tick_modifiers(self):
        """Обновить все временные модификаторы (вызывается каждый ход)"""
        for modifier in self.modifiers:
            modifier.tick()
        
        # Удалить истёкшие модификаторы
        self.modifiers = [m for m in self.modifiers if not m.is_expired()]
    
    def get_modifiers_for_stat(self, stat_name: str) -> List[StatModifier]:
        """
        Получить все модификаторы для конкретной характеристики
        
        Args:
            stat_name: Название характеристики
            
        Returns:
            Список модификаторов
        """
        return [m for m in self.modifiers if m.stat_name == stat_name]
    
    def calculate_modified_value(self, base_value: float, stat_name: str) -> float:
        """
        Рассчитать модифицированное значение характеристики
        
        Порядок применения:
        1. FLAT модификаторы (сложение)
        2. PERCENT модификаторы (процентное увеличение от базы)
        3. MULTIPLY модификаторы (умножение)
        
        Args:
            base_value: Базовое значение характеристики
            stat_name: Название характеристики
            
        Returns:
            Модифицированное значение
        """
        result = base_value
        modifiers = self.get_modifiers_for_stat(stat_name)
        
        # 1. Применить FLAT модификаторы
        flat_bonus = sum(m.value for m in modifiers if m.modifier_type == ModifierType.FLAT)
        result += flat_bonus
        
        # 2. Применить PERCENT модификаторы (от базового значения)
        percent_bonus = sum(m.value for m in modifiers if m.modifier_type == ModifierType.PERCENT)
        result += base_value * percent_bonus
        
        # 3. Применить MULTIPLY модификаторы
        for modifier in modifiers:
            if modifier.modifier_type == ModifierType.MULTIPLY:
                result *= modifier.value
        
        return result
    
    def get_modifier_summary(self, stat_name: str) -> Dict[str, float]:
        """
        Получить сводку модификаторов для характеристики
        
        Args:
            stat_name: Название характеристики
            
        Returns:
            Словарь с суммами по типам модификаторов
        """
        modifiers = self.get_modifiers_for_stat(stat_name)
        
        return {
            'flat': sum(m.value for m in modifiers if m.modifier_type == ModifierType.FLAT),
            'percent': sum(m.value for m in modifiers if m.modifier_type == ModifierType.PERCENT),
            'multiply': sum(m.value for m in modifiers if m.modifier_type == ModifierType.MULTIPLY)
        }
    
    def has_modifier(self, source_id: str) -> bool:
        """
        Проверить, есть ли модификатор с данным ID
        
        Args:
            source_id: ID источника модификатора
            
        Returns:
            True если модификатор существует
        """
        return any(m.source_id == source_id for m in self.modifiers)
    
    def get_all_active_modifiers(self) -> List[StatModifier]:
        """Получить все активные модификаторы"""
        return self.modifiers.copy()
    
    def clear_temporary_modifiers(self):
        """Удалить все временные модификаторы"""
        self.modifiers = [m for m in self.modifiers if m.is_permanent()]
    
    def to_dict(self) -> dict:
        """Сериализация"""
        return {
            'modifiers': [m.to_dict() for m in self.modifiers]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ModifierManager':
        """Десериализация"""
        manager = cls()
        manager.modifiers = [StatModifier.from_dict(m) for m in data.get('modifiers', [])]
        return manager


# Примеры создания модификаторов
def create_ability_modifier(stat_name: str, value: float, modifier_type: ModifierType, 
                           ability_id: str, description: str = "") -> StatModifier:
    """Создать модификатор от способности"""
    return StatModifier(
        stat_name=stat_name,
        value=value,
        modifier_type=modifier_type,
        source=ModifierSource.ABILITY,
        source_id=f"ability_{ability_id}",
        duration=-1,  # Постоянный
        description=description
    )


def create_item_modifier(stat_name: str, value: float, modifier_type: ModifierType,
                        item_id: str, description: str = "") -> StatModifier:
    """Создать модификатор от предмета"""
    return StatModifier(
        stat_name=stat_name,
        value=value,
        modifier_type=modifier_type,
        source=ModifierSource.ITEM,
        source_id=f"item_{item_id}",
        duration=-1,  # Постоянный пока предмет экипирован
        description=description
    )


def create_buff_modifier(stat_name: str, value: float, modifier_type: ModifierType,
                        buff_id: str, duration: int, description: str = "") -> StatModifier:
    """Создать временный бафф"""
    return StatModifier(
        stat_name=stat_name,
        value=value,
        modifier_type=modifier_type,
        source=ModifierSource.BUFF,
        source_id=f"buff_{buff_id}",
        duration=duration,
        description=description
    )


def create_research_modifier(stat_name: str, value: float, modifier_type: ModifierType,
                            research_id: str, description: str = "") -> StatModifier:
    """Создать модификатор от исследования"""
    return StatModifier(
        stat_name=stat_name,
        value=value,
        modifier_type=modifier_type,
        source=ModifierSource.RESEARCH,
        source_id=f"research_{research_id}",
        duration=-1,  # Постоянный
        description=description
    )
