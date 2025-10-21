"""
Предустановленные способности
Версия: 0.4.0
Этап 0, Неделя 2
"""

from .abilities import Ability, AbilityType, AbilityCategory, AbilityRequirement
from .modifiers import StatModifier, ModifierType, ModifierSource


def create_combat_abilities():
    """Создать боевые способности"""
    abilities = []
    
    # Tier 1 - Базовые боевые способности
    abilities.append(Ability(
        id="combat_basic",
        name="Боевая подготовка",
        description="Базовые навыки боя. +3 к атаке",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="attack",
                value=3,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_combat_basic",
                description="Боевая подготовка +3"
            )
        ],
        tier=1
    ))
    
    abilities.append(Ability(
        id="tough",
        name="Живучесть",
        description="Повышенная выносливость. +20 к максимальному здоровью",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="max_health",
                value=20,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_tough",
                description="Живучесть +20 HP"
            )
        ],
        tier=1
    ))
    
    # Tier 2 - Продвинутые боевые способности
    abilities.append(Ability(
        id="combat_advanced",
        name="Мастер боя",
        description="Продвинутые боевые техники. +5 к атаке, +10% точность",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(
            required_level=3,
            required_abilities=["combat_basic"]
        ),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="attack",
                value=5,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_combat_advanced",
                description="Мастер боя +5"
            ),
            StatModifier(
                stat_name="accuracy",
                value=0.1,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_combat_advanced_acc",
                description="Мастер боя +10% точность"
            )
        ],
        tier=2
    ))
    
    abilities.append(Ability(
        id="critical_strike",
        name="Критический удар",
        description="Увеличивает шанс и урон критических ударов. +10% шанс, +50% урон",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(
            required_level=3,
            required_abilities=["combat_basic"]
        ),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="critical_chance",
                value=0.1,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_critical_strike",
                description="Критический удар +10%"
            ),
            StatModifier(
                stat_name="critical_damage",
                value=0.5,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_critical_damage",
                description="Критический урон +50%"
            )
        ],
        tier=2
    ))
    
    # Tier 3 - Экспертные боевые способности
    abilities.append(Ability(
        id="berserker",
        name="Берсерк",
        description="Переключаемая ярость. +50% к атаке, -20% к защите",
        ability_type=AbilityType.TOGGLE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(
            required_level=5,
            required_abilities=["combat_advanced"]
        ),
        cost=2,
        stat_modifiers=[
            StatModifier(
                stat_name="attack",
                value=0.5,
                modifier_type=ModifierType.PERCENT,
                source=ModifierSource.ABILITY,
                source_id="ability_berserker_atk",
                description="Берсерк +50% атака"
            ),
            StatModifier(
                stat_name="defense",
                value=-0.2,
                modifier_type=ModifierType.PERCENT,
                source=ModifierSource.ABILITY,
                source_id="ability_berserker_def",
                description="Берсерк -20% защита"
            )
        ],
        tier=3
    ))
    
    return abilities


def create_survival_abilities():
    """Создать способности выживания"""
    abilities = []
    
    # Tier 1
    abilities.append(Ability(
        id="iron_skin",
        name="Железная кожа",
        description="Укрепляет защиту. +3 к защите",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.SURVIVAL,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="defense",
                value=3,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_iron_skin",
                description="Железная кожа +3"
            )
        ],
        tier=1
    ))
    
    abilities.append(Ability(
        id="evasion_basic",
        name="Уклонение",
        description="Базовые навыки уклонения. +5% к уклонению",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.SURVIVAL,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="evasion",
                value=0.05,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_evasion_basic",
                description="Уклонение +5%"
            )
        ],
        tier=1
    ))
    
    # Tier 2
    abilities.append(Ability(
        id="regeneration",
        name="Регенерация",
        description="Быстрое восстановление. +50 к максимальному здоровью",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.SURVIVAL,
        requirements=AbilityRequirement(
            required_level=3,
            required_abilities=["iron_skin"]
        ),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="max_health",
                value=50,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_regeneration",
                description="Регенерация +50 HP"
            )
        ],
        tier=2
    ))
    
    return abilities


def create_exploration_abilities():
    """Создать способности исследования"""
    abilities = []
    
    # Tier 1
    abilities.append(Ability(
        id="keen_eye",
        name="Зоркий глаз",
        description="Улучшенное восприятие. +2 к восприятию",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.EXPLORATION,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="perception",
                value=2,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_keen_eye",
                description="Зоркий глаз +2"
            )
        ],
        tier=1
    ))
    
    abilities.append(Ability(
        id="lucky",
        name="Везунчик",
        description="Повышенная удача. +2 к удаче",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.EXPLORATION,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="luck",
                value=2,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_lucky",
                description="Везунчик +2"
            )
        ],
        tier=1
    ))
    
    # Tier 2
    abilities.append(Ability(
        id="treasure_hunter",
        name="Охотник за сокровищами",
        description="Мастер поиска. +3 к восприятию, +3 к удаче",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.EXPLORATION,
        requirements=AbilityRequirement(
            required_level=3,
            required_abilities=["keen_eye", "lucky"]
        ),
        cost=2,
        stat_modifiers=[
            StatModifier(
                stat_name="perception",
                value=3,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_treasure_hunter_per",
                description="Охотник за сокровищами +3 восприятие"
            ),
            StatModifier(
                stat_name="luck",
                value=3,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_treasure_hunter_luck",
                description="Охотник за сокровищами +3 удача"
            )
        ],
        tier=2
    ))
    
    return abilities


def create_crafting_abilities():
    """Создать способности крафта"""
    abilities = []
    
    # Tier 1
    abilities.append(Ability(
        id="crafting_basic",
        name="Основы крафта",
        description="Базовые навыки создания предметов. +2 к интеллекту",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.CRAFTING,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="intelligence",
                value=2,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_crafting_basic",
                description="Основы крафта +2"
            )
        ],
        tier=1
    ))
    
    # Tier 2
    abilities.append(Ability(
        id="master_craftsman",
        name="Мастер-ремесленник",
        description="Экспертные навыки крафта. +5 к интеллекту",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.CRAFTING,
        requirements=AbilityRequirement(
            required_level=3,
            required_abilities=["crafting_basic"]
        ),
        cost=1,
        stat_modifiers=[
            StatModifier(
                stat_name="intelligence",
                value=5,
                modifier_type=ModifierType.FLAT,
                source=ModifierSource.ABILITY,
                source_id="ability_master_craftsman",
                description="Мастер-ремесленник +5"
            )
        ],
        tier=2
    ))
    
    return abilities


def create_all_abilities():
    """Создать все предустановленные способности"""
    all_abilities = []
    all_abilities.extend(create_combat_abilities())
    all_abilities.extend(create_survival_abilities())
    all_abilities.extend(create_exploration_abilities())
    all_abilities.extend(create_crafting_abilities())
    return all_abilities
