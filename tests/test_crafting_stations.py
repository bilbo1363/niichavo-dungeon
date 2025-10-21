"""
Тесты для системы крафт-станций
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.objects.crafting_stations import (
    CraftingStation, StationType, StationCategory,
    StationUpgrade, StationManager
)
from src.objects.station_presets import (
    create_workbench, create_laboratory, create_alchemy_table,
    create_magic_circle, create_aldan_terminal, create_all_stations
)


def test_station_creation():
    """Тест создания станции"""
    station = CraftingStation(
        id="test_station",
        station_type=StationType.WORKBENCH,
        category=StationCategory.BASIC,
        name="Тестовая станция",
        description="Описание",
    )
    
    assert station.id == "test_station"
    assert station.station_type == StationType.WORKBENCH
    assert station.current_tier == 1
    assert not station.is_unlocked
    print("✅ test_station_creation пройден")


def test_station_upgrade():
    """Тест улучшения станции"""
    station = create_workbench()
    
    # Проверяем начальный уровень
    assert station.current_tier == 1
    
    # Проверяем, что можем улучшить (с достаточными ресурсами)
    player_inventory = {
        "iron_ingot": 10,
        "wooden_plank": 20,
        "rope": 5,
    }
    assert station.can_upgrade(5, player_inventory, 500)
    
    # Улучшаем
    success = station.upgrade()
    assert success
    assert station.current_tier == 2
    
    print("✅ test_station_upgrade пройден")


def test_cannot_upgrade_without_requirements():
    """Тест невозможности улучшения без требований"""
    station = create_workbench()
    
    # Недостаточно материалов
    player_inventory = {"iron_ingot": 1}
    assert not station.can_upgrade(5, player_inventory, 500)
    
    # Недостаточно денег
    player_inventory = {
        "iron_ingot": 10,
        "wooden_plank": 20,
        "rope": 5,
    }
    assert not station.can_upgrade(5, player_inventory, 100)
    
    # Недостаточный уровень
    assert not station.can_upgrade(1, player_inventory, 500)
    
    print("✅ test_cannot_upgrade_without_requirements пройден")


def test_crafting_speed_bonus():
    """Тест бонуса скорости крафта"""
    station = create_workbench()
    
    # Tier 1: нет бонуса
    assert station.get_crafting_speed_multiplier() == 1.0
    
    # Улучшаем до Tier 2
    station.current_tier = 2
    # Tier 2: +20% скорости
    assert abs(station.get_crafting_speed_multiplier() - 1.2) < 0.01
    
    # Улучшаем до Tier 3
    station.current_tier = 3
    # Tier 3: +20% + +30% = +50% скорости
    assert abs(station.get_crafting_speed_multiplier() - 1.5) < 0.01
    
    print("✅ test_crafting_speed_bonus пройден")


def test_quality_bonus():
    """Тест бонуса качества"""
    station = create_workbench()
    
    # Tier 1: нет бонуса
    assert station.get_quality_bonus() == 0.0
    
    # Tier 2: +10% качества
    station.current_tier = 2
    assert abs(station.get_quality_bonus() - 0.1) < 0.01
    
    # Tier 3: +10% + +15% = +25% качества
    station.current_tier = 3
    assert abs(station.get_quality_bonus() - 0.25) < 0.01
    
    print("✅ test_quality_bonus пройден")


def test_unlocked_recipes():
    """Тест разблокированных рецептов"""
    station = create_workbench()
    
    # Tier 1: 4 рецепта
    recipes = station.get_unlocked_recipes()
    assert len(recipes) == 4
    assert "wooden_stick" in recipes
    
    # Tier 2: 4 + 4 = 8 рецептов
    station.current_tier = 2
    recipes = station.get_unlocked_recipes()
    assert len(recipes) == 8
    assert "iron_sword" in recipes
    
    # Tier 3: 8 + 4 = 12 рецептов
    station.current_tier = 3
    recipes = station.get_unlocked_recipes()
    assert len(recipes) == 12
    assert "steel_sword" in recipes
    
    print("✅ test_unlocked_recipes пройден")


def test_station_manager():
    """Тест менеджера станций"""
    manager = StationManager()
    
    # Добавляем станцию
    workbench = create_workbench()
    manager.add_station(workbench)
    
    # Проверяем, что станция добавлена
    assert manager.get_station("workbench") is not None
    assert len(manager.get_unlocked_stations()) == 1
    
    # Добавляем ещё станцию
    lab = create_laboratory()
    manager.add_station(lab)
    
    # Лаборатория не разблокирована
    assert len(manager.get_unlocked_stations()) == 1
    
    # Разблокируем лабораторию
    manager.unlock_station("laboratory")
    assert len(manager.get_unlocked_stations()) == 2
    
    print("✅ test_station_manager пройден")


def test_all_stations_creation():
    """Тест создания всех станций"""
    manager = create_all_stations()
    
    # Проверяем, что все станции созданы
    assert len(manager.stations) == 5
    
    # Проверяем типы станций
    assert manager.get_station("workbench") is not None
    assert manager.get_station("laboratory") is not None
    assert manager.get_station("alchemy_table") is not None
    assert manager.get_station("magic_circle") is not None
    assert manager.get_station("aldan_terminal") is not None
    
    # Только верстак разблокирован по умолчанию
    assert len(manager.get_unlocked_stations()) == 1
    
    print("✅ test_all_stations_creation пройден")


def test_station_serialization():
    """Тест сериализации станции"""
    station = create_workbench()
    station.current_tier = 2
    
    # Сериализуем
    data = station.to_dict()
    
    # Десериализуем
    restored = CraftingStation.from_dict(data)
    
    # Проверяем
    assert restored.id == station.id
    assert restored.station_type == station.station_type
    assert restored.current_tier == station.current_tier
    assert len(restored.upgrades) == len(station.upgrades)
    
    print("✅ test_station_serialization пройден")


def test_manager_serialization():
    """Тест сериализации менеджера"""
    manager = create_all_stations()
    manager.unlock_station("laboratory")
    
    # Сериализуем
    data = manager.to_dict()
    
    # Десериализуем
    restored = StationManager.from_dict(data)
    
    # Проверяем
    assert len(restored.stations) == len(manager.stations)
    assert len(restored.unlocked_stations) == len(manager.unlocked_stations)
    assert "laboratory" in restored.unlocked_stations
    
    print("✅ test_manager_serialization пройден")


def run_all_tests():
    """Запустить все тесты"""
    print("\n🧪 Запуск тестов крафт-станций...\n")
    
    test_station_creation()
    test_station_upgrade()
    test_cannot_upgrade_without_requirements()
    test_crafting_speed_bonus()
    test_quality_bonus()
    test_unlocked_recipes()
    test_station_manager()
    test_all_stations_creation()
    test_station_serialization()
    test_manager_serialization()
    
    print("\n✅ Все тесты пройдены успешно!\n")


if __name__ == "__main__":
    run_all_tests()
