"""
Игровые системы
Версия: 0.4.0
"""

from .stats import PlayerStats, get_stats_for_difficulty, DIFFICULTY_PRESETS
from .level_system import LevelSystem, ExperienceRewards, LEVEL_TABLE
from .modifiers import (
    StatModifier,
    ModifierManager,
    ModifierType,
    ModifierSource,
    create_ability_modifier,
    create_item_modifier,
    create_buff_modifier,
    create_research_modifier
)

__all__ = [
    # Stats
    'PlayerStats',
    'get_stats_for_difficulty',
    'DIFFICULTY_PRESETS',
    
    # Level System
    'LevelSystem',
    'ExperienceRewards',
    'LEVEL_TABLE',
    
    # Modifiers
    'StatModifier',
    'ModifierManager',
    'ModifierType',
    'ModifierSource',
    'create_ability_modifier',
    'create_item_modifier',
    'create_buff_modifier',
    'create_research_modifier',
]
