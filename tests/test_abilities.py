"""
Тесты для системы способностей
Версия: 0.4.0
"""

import sys
sys.path.insert(0, 'src')

from systems import (
    Ability,
    AbilityTree,
    AbilityType,
    AbilityCategory,
    AbilityRequirement,
    create_all_abilities,
    PlayerStats,
    ModifierManager
)


def test_ability_requirements():
    """Тест требований способностей"""
    print("=== Тест AbilityRequirement ===")
    
    # Простое требование - только уровень
    req1 = AbilityRequirement(required_level=3)
    print(f"Требование: уровень 3")
    print(f"  Уровень 2: {req1.is_met(2, set(), {})}")  # False
    print(f"  Уровень 3: {req1.is_met(3, set(), {})}")  # True
    
    # Требование с другими способностями
    req2 = AbilityRequirement(
        required_level=5,
        required_abilities=["combat_basic"]
    )
    print(f"\nТребование: уровень 5 + combat_basic")
    print(f"  Уровень 5, нет способности: {req2.is_met(5, set(), {})}")  # False
    print(f"  Уровень 5, есть способность: {req2.is_met(5, {'combat_basic'}, {})}")  # True
    
    # Требование с характеристиками
    req3 = AbilityRequirement(
        required_level=3,
        required_stats={'attack': 15}
    )
    print(f"\nТребование: уровень 3 + атака 15")
    print(f"  Атака 10: {req3.is_met(3, set(), {'attack': 10})}")  # False
    print(f"  Атака 15: {req3.is_met(3, set(), {'attack': 15})}")  # True
    print()


def test_ability_tree():
    """Тест дерева способностей"""
    print("=== Тест AbilityTree ===")
    
    tree = AbilityTree()
    
    # Создать тестовые способности
    ability1 = Ability(
        id="test_basic",
        name="Базовая способность",
        description="Тестовая способность",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        tier=1
    )
    
    ability2 = Ability(
        id="test_advanced",
        name="Продвинутая способность",
        description="Требует базовую",
        ability_type=AbilityType.PASSIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(
            required_level=3,
            required_abilities=["test_basic"]
        ),
        cost=1,
        tier=2
    )
    
    # Зарегистрировать способности
    tree.register_ability(ability1)
    tree.register_ability(ability2)
    
    print(f"Зарегистрировано способностей: {len(tree.abilities)}")
    
    # Проверка разблокировки
    stats = {'attack': 10}
    
    print(f"\nУровень 1, 1 очко:")
    print(f"  Можно разблокировать test_basic: {tree.can_unlock('test_basic', 1, stats, 1)}")
    print(f"  Можно разблокировать test_advanced: {tree.can_unlock('test_advanced', 1, stats, 1)}")
    
    # Разблокировать базовую
    tree.unlock('test_basic')
    print(f"\nРазблокирована test_basic")
    print(f"  Разблокировано способностей: {len(tree.unlocked)}")
    
    print(f"\nУровень 3, 1 очко:")
    print(f"  Можно разблокировать test_advanced: {tree.can_unlock('test_advanced', 3, stats, 1)}")
    
    # Разблокировать продвинутую
    tree.unlock('test_advanced')
    print(f"\nРазблокирована test_advanced")
    print(f"  Разблокировано способностей: {len(tree.unlocked)}")
    print()


def test_ability_presets():
    """Тест предустановленных способностей"""
    print("=== Тест предустановленных способностей ===")
    
    abilities = create_all_abilities()
    print(f"Всего способностей: {len(abilities)}")
    
    # Группировка по категориям
    by_category = {}
    for ability in abilities:
        cat = ability.category.value
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nПо категориям:")
    for cat, count in by_category.items():
        print(f"  {cat}: {count}")
    
    # Группировка по уровням
    by_tier = {}
    for ability in abilities:
        tier = ability.tier
        by_tier[tier] = by_tier.get(tier, 0) + 1
    
    print("\nПо уровням дерева:")
    for tier in sorted(by_tier.keys()):
        print(f"  Tier {tier}: {by_tier[tier]}")
    
    # Показать несколько примеров
    print("\nПримеры способностей:")
    for ability in abilities[:3]:
        print(f"  - {ability.name} ({ability.category.value}, tier {ability.tier})")
        print(f"    {ability.description}")
        if ability.stat_modifiers:
            print(f"    Модификаторы: {len(ability.stat_modifiers)}")
    print()


def test_ability_toggle():
    """Тест переключаемых способностей"""
    print("=== Тест переключаемых способностей ===")
    
    tree = AbilityTree()
    
    # Создать переключаемую способность
    toggle_ability = Ability(
        id="test_toggle",
        name="Переключаемая",
        description="Тест переключения",
        ability_type=AbilityType.TOGGLE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        tier=1
    )
    
    tree.register_ability(toggle_ability)
    tree.unlock('test_toggle')
    
    print(f"Способность разблокирована")
    print(f"  Активна: {tree.is_active('test_toggle')}")
    
    # Включить
    tree.toggle_ability('test_toggle')
    print(f"\nПосле включения:")
    print(f"  Активна: {tree.is_active('test_toggle')}")
    
    # Выключить
    tree.toggle_ability('test_toggle')
    print(f"\nПосле выключения:")
    print(f"  Активна: {tree.is_active('test_toggle')}")
    print()


def test_ability_cooldowns():
    """Тест перезарядки способностей"""
    print("=== Тест перезарядки способностей ===")
    
    tree = AbilityTree()
    
    # Создать активную способность с перезарядкой
    active_ability = Ability(
        id="test_active",
        name="Активная способность",
        description="С перезарядкой",
        ability_type=AbilityType.ACTIVE,
        category=AbilityCategory.COMBAT,
        requirements=AbilityRequirement(required_level=1),
        cost=1,
        cooldown=3,
        tier=1
    )
    
    tree.register_ability(active_ability)
    tree.unlock('test_active')
    
    print(f"Способность разблокирована (перезарядка: 3 хода)")
    
    # Использовать
    result = tree.use_ability('test_active')
    print(f"\nПервое использование: {result}")
    print(f"  Текущая перезарядка: {tree.get_cooldown('test_active')}")
    
    # Попытка использовать снова
    result = tree.use_ability('test_active')
    print(f"\nПопытка использовать снова: {result}")
    
    # Обновить перезарядки
    for i in range(3):
        tree.update_cooldowns()
        cd = tree.get_cooldown('test_active')
        print(f"  После хода {i+1}: перезарядка {cd}")
    
    # Использовать снова
    result = tree.use_ability('test_active')
    print(f"\nИспользование после перезарядки: {result}")
    print()


def test_ability_modifiers_integration():
    """Тест интеграции способностей с модификаторами"""
    print("=== Тест интеграции с модификаторами ===")
    
    # Создать дерево с реальными способностями
    tree = AbilityTree()
    abilities = create_all_abilities()
    
    for ability in abilities:
        tree.register_ability(ability)
    
    # Разблокировать несколько способностей
    tree.unlock('combat_basic')  # +3 к атаке
    tree.unlock('tough')         # +20 к здоровью
    tree.unlock('keen_eye')      # +2 к восприятию
    
    print(f"Разблокировано способностей: {len(tree.unlocked)}")
    
    # Получить все модификаторы
    modifiers = tree.get_all_stat_modifiers()
    print(f"Всего модификаторов: {len(modifiers)}")
    
    # Применить к характеристикам
    stats = PlayerStats()
    modifier_manager = ModifierManager()
    
    for mod in modifiers:
        modifier_manager.add_modifier(mod)
    
    print(f"\nБазовые характеристики:")
    print(f"  Атака: {stats.attack}")
    print(f"  Здоровье: {stats.max_health}")
    print(f"  Восприятие: {stats.perception}")
    
    print(f"\nС модификаторами:")
    print(f"  Атака: {modifier_manager.calculate_modified_value(stats.attack, 'attack')}")
    print(f"  Здоровье: {modifier_manager.calculate_modified_value(stats.max_health, 'max_health')}")
    print(f"  Восприятие: {modifier_manager.calculate_modified_value(stats.perception, 'perception')}")
    print()


def test_save_load():
    """Тест сохранения/загрузки"""
    print("=== Тест сохранения/загрузки ===")
    
    # Создать дерево
    tree = AbilityTree()
    abilities = create_all_abilities()
    
    for ability in abilities:
        tree.register_ability(ability)
    
    # Разблокировать способности
    tree.unlock('combat_basic')
    tree.unlock('tough')
    tree.unlock('berserker')
    tree.toggle_ability('berserker')  # Включить переключаемую
    
    print(f"Исходное дерево:")
    print(f"  Разблокировано: {len(tree.unlocked)}")
    print(f"  Активных toggle: {len(tree.active_toggles)}")
    
    # Сохранить
    save_data = tree.to_dict()
    print(f"\nДанные сохранены: {len(str(save_data))} символов")
    
    # Загрузить
    abilities_dict = {a.id: a for a in abilities}
    tree2 = AbilityTree.from_dict(save_data, abilities_dict)
    
    print(f"\nЗагруженное дерево:")
    print(f"  Разблокировано: {len(tree2.unlocked)}")
    print(f"  Активных toggle: {len(tree2.active_toggles)}")
    print(f"  Способности совпадают: {tree.unlocked == tree2.unlocked}")
    print()


if __name__ == '__main__':
    test_ability_requirements()
    test_ability_tree()
    test_ability_presets()
    test_ability_toggle()
    test_ability_cooldowns()
    test_ability_modifiers_integration()
    test_save_load()
    
    print("=== Все тесты завершены ===")
