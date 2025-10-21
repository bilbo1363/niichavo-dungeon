"""
Тесты для системы характеристик
Версия: 0.4.0
"""

import sys
sys.path.insert(0, 'src')

from systems import (
    PlayerStats,
    LevelSystem,
    ModifierManager,
    ModifierType,
    ModifierSource,
    create_ability_modifier,
    ExperienceRewards
)


def test_player_stats():
    """Тест базовых характеристик"""
    print("=== Тест PlayerStats ===")
    
    stats = PlayerStats()
    print(f"Начальное здоровье: {stats.health}/{stats.max_health}")
    print(f"Атака: {stats.attack}, Защита: {stats.defense}")
    print(f"Восприятие: {stats.perception}, Интеллект: {stats.intelligence}, Удача: {stats.luck}")
    
    # Тест получения урона
    damage = stats.take_damage(20)
    print(f"\nПолучен урон 20, фактический урон: {damage}")
    print(f"Здоровье после урона: {stats.health}/{stats.max_health}")
    
    # Тест лечения
    healed = stats.heal(30)
    print(f"Восстановлено здоровья: {healed}")
    print(f"Здоровье после лечения: {stats.health}/{stats.max_health}")
    
    print(f"Игрок жив: {stats.is_alive()}")
    print()


def test_level_system():
    """Тест системы уровней"""
    print("=== Тест LevelSystem ===")
    
    level_system = LevelSystem()
    print(f"Начальный уровень: {level_system.level}")
    print(f"Опыт: {level_system.experience}/{level_system.exp_to_next_level}")
    print(f"Очки способностей: {level_system.ability_points}")
    
    # Получение опыта
    print("\nПолучение 150 опыта...")
    levels_gained = level_system.gain_exp(150)
    print(f"Получено уровней: {levels_gained}")
    print(f"Текущий уровень: {level_system.level}")
    print(f"Опыт: {level_system.experience}/{level_system.exp_to_next_level}")
    print(f"Прогресс: {level_system.get_level_progress_percent()}%")
    print(f"Очки способностей: {level_system.ability_points}")
    
    # Получение большого количества опыта
    print("\nПолучение 1000 опыта...")
    levels_gained = level_system.gain_exp(1000)
    print(f"Получено уровней: {levels_gained}")
    print(f"Текущий уровень: {level_system.level}")
    print(f"Очки способностей: {level_system.ability_points}")
    print()


def test_modifiers():
    """Тест системы модификаторов"""
    print("=== Тест ModifierManager ===")
    
    manager = ModifierManager()
    stats = PlayerStats()
    
    print(f"Базовая атака: {stats.attack}")
    
    # Добавить модификаторы
    # +5 к атаке (flat)
    manager.add_modifier(create_ability_modifier(
        'attack', 5, ModifierType.FLAT, 'basic_combat', "+5 к атаке"
    ))
    
    # +20% к атаке (percent)
    manager.add_modifier(create_ability_modifier(
        'attack', 0.2, ModifierType.PERCENT, 'advanced_combat', "+20% к атаке"
    ))
    
    # x1.5 к атаке (multiply)
    manager.add_modifier(create_ability_modifier(
        'attack', 1.5, ModifierType.MULTIPLY, 'berserker', "x1.5 к атаке"
    ))
    
    # Рассчитать модифицированное значение
    modified_attack = manager.calculate_modified_value(stats.attack, 'attack')
    print(f"Модифицированная атака: {modified_attack}")
    
    # Показать сводку
    summary = manager.get_modifier_summary('attack')
    print(f"Сводка модификаторов: {summary}")
    
    # Показать все модификаторы
    print("\nАктивные модификаторы:")
    for mod in manager.get_all_active_modifiers():
        print(f"  - {mod.description} (источник: {mod.source.value}, ID: {mod.source_id})")
    print()


def test_experience_rewards():
    """Тест наград опытом"""
    print("=== Тест ExperienceRewards ===")
    
    print(f"Опыт за убийство врага 1 уровня: {ExperienceRewards.calculate_enemy_exp(1)}")
    print(f"Опыт за убийство врага 5 уровня: {ExperienceRewards.calculate_enemy_exp(5)}")
    print(f"Опыт за убийство врага 10 уровня: {ExperienceRewards.calculate_enemy_exp(10)}")
    
    print(f"\nОпыт за прохождение 1 этажа: {ExperienceRewards.calculate_floor_completion_exp(1)}")
    print(f"Опыт за прохождение 5 этажа: {ExperienceRewards.calculate_floor_completion_exp(5)}")
    print(f"Опыт за прохождение 10 этажа: {ExperienceRewards.calculate_floor_completion_exp(10)}")
    
    print(f"\nОпыт за открытие комнаты: {ExperienceRewards.DISCOVER_ROOM}")
    print(f"Опыт за нахождение секрета: {ExperienceRewards.DISCOVER_SECRET}")
    print(f"Опыт за крафт предмета: {ExperienceRewards.CRAFT_ITEM}")
    print()


def test_integration():
    """Тест интеграции систем"""
    print("=== Тест интеграции систем ===")
    
    # Создать игрока
    stats = PlayerStats()
    level_system = LevelSystem()
    modifier_manager = ModifierManager()
    
    print(f"Игрок создан: Уровень {level_system.level}, Атака {stats.attack}")
    
    # Добавить модификатор от способности
    modifier_manager.add_modifier(create_ability_modifier(
        'attack', 3, ModifierType.FLAT, 'combat_training', "Боевая подготовка"
    ))
    
    modified_attack = modifier_manager.calculate_modified_value(stats.attack, 'attack')
    print(f"Атака с модификаторами: {modified_attack}")
    
    # Получить опыт
    print("\nУбит враг 3 уровня...")
    exp_gained = ExperienceRewards.calculate_enemy_exp(3)
    levels = level_system.gain_exp(exp_gained)
    
    if levels:
        print(f"Получен уровень {levels[0]}!")
        print(f"Доступно очков способностей: {level_system.ability_points}")
    
    # Сохранение
    print("\nСохранение состояния...")
    save_data = {
        'stats': stats.to_dict(),
        'level': level_system.to_dict(),
        'modifiers': modifier_manager.to_dict()
    }
    print(f"Данные сохранены: {len(str(save_data))} символов")
    print()


if __name__ == '__main__':
    test_player_stats()
    test_level_system()
    test_modifiers()
    test_experience_rewards()
    test_integration()
    
    print("=== Все тесты завершены ===")
