"""
Тесты для системы крафта
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.systems.crafting import (
    Recipe, RecipeCategory, CraftingDifficulty,
    CraftingSystem, CraftingResult
)
from src.systems.recipe_presets import (
    create_workbench_recipes, create_laboratory_recipes,
    create_all_recipes
)


def test_recipe_creation():
    """Тест создания рецепта"""
    recipe = Recipe(
        id="test_recipe",
        name="Тестовый рецепт",
        description="Описание",
        category=RecipeCategory.TOOLS,
        required_station="workbench",
        required_station_tier=1,
        ingredients={"wood": 2},
        result_item="test_item",
    )
    
    assert recipe.id == "test_recipe"
    assert recipe.category == RecipeCategory.TOOLS
    assert recipe.ingredients["wood"] == 2
    print("✅ test_recipe_creation пройден")


def test_can_craft():
    """Тест проверки возможности крафта"""
    recipe = Recipe(
        id="iron_sword",
        name="Железный меч",
        description="Меч",
        category=RecipeCategory.WEAPONS,
        required_station="workbench",
        required_station_tier=2,
        required_level=5,
        ingredients={"iron_ingot": 3, "wooden_stick": 1},
        result_item="iron_sword",
    )
    
    # Достаточно ресурсов
    inventory = {"iron_ingot": 3, "wooden_stick": 1}
    assert recipe.can_craft(5, inventory, "workbench", 2)
    
    # Недостаточно уровня
    assert not recipe.can_craft(3, inventory, "workbench", 2)
    
    # Недостаточно tier станции
    assert not recipe.can_craft(5, inventory, "workbench", 1)
    
    # Недостаточно ресурсов
    inventory_low = {"iron_ingot": 1}
    assert not recipe.can_craft(5, inventory_low, "workbench", 2)
    
    print("✅ test_can_craft пройден")


def test_crafting_system():
    """Тест системы крафта"""
    system = CraftingSystem()
    
    recipe = Recipe(
        id="test_item",
        name="Тестовый предмет",
        description="Описание",
        category=RecipeCategory.TOOLS,
        required_station="workbench",
        ingredients={"wood": 1},
        result_item="test_item",
    )
    
    # Добавляем рецепт
    system.add_recipe(recipe)
    assert system.get_recipe("test_item") is not None
    
    # Разблокируем рецепт
    system.unlock_recipe("test_item")
    assert "test_item" in system.unlocked_recipes
    
    print("✅ test_crafting_system пройден")


def test_craft_item_success():
    """Тест успешного крафта"""
    system = CraftingSystem()
    
    recipe = Recipe(
        id="wooden_stick",
        name="Деревянная палка",
        description="Палка",
        category=RecipeCategory.MATERIALS,
        required_station="workbench",
        ingredients={"wood": 1},
        result_item="wooden_stick",
        result_count=4,
        success_chance=1.0,  # 100% успех
    )
    
    system.add_recipe(recipe)
    system.unlock_recipe("wooden_stick")
    
    inventory = {"wood": 5}
    result = system.craft_item(
        "wooden_stick",
        player_level=1,
        player_inventory=inventory,
        station_id="workbench",
        station_tier=1
    )
    
    assert result.success
    assert result.result_item == "wooden_stick"
    assert result.result_count == 4
    assert inventory["wood"] == 4  # Потрачено 1
    
    print("✅ test_craft_item_success пройден")


def test_craft_item_not_unlocked():
    """Тест крафта неразблокированного рецепта"""
    system = CraftingSystem()
    
    recipe = Recipe(
        id="test_item",
        name="Тестовый предмет",
        description="Описание",
        category=RecipeCategory.TOOLS,
        required_station="workbench",
        ingredients={"wood": 1},
        result_item="test_item",
    )
    
    system.add_recipe(recipe)
    # НЕ разблокируем рецепт
    
    inventory = {"wood": 5}
    result = system.craft_item(
        "test_item",
        player_level=1,
        player_inventory=inventory,
        station_id="workbench",
        station_tier=1
    )
    
    assert not result.success
    assert "не разблокирован" in result.message
    
    print("✅ test_craft_item_not_unlocked пройден")


def test_craft_with_quality_bonus():
    """Тест крафта с бонусом качества"""
    system = CraftingSystem()
    
    recipe = Recipe(
        id="iron_sword",
        name="Железный меч",
        description="Меч",
        category=RecipeCategory.WEAPONS,
        required_station="workbench",
        ingredients={"iron_ingot": 3},
        result_item="iron_sword",
        success_chance=1.0,
        quality_bonus_item="iron_sword_sharp",
        quality_bonus_chance=1.0,  # 100% бонус для теста
    )
    
    system.add_recipe(recipe)
    system.unlock_recipe("iron_sword")
    
    inventory = {"iron_ingot": 10}
    result = system.craft_item(
        "iron_sword",
        player_level=5,
        player_inventory=inventory,
        station_id="workbench",
        station_tier=2,
        quality_bonus=0.0
    )
    
    assert result.success
    assert result.bonus_item == "iron_sword_sharp"
    assert result.bonus_count == 1
    
    print("✅ test_craft_with_quality_bonus пройден")


def test_get_recipes_for_station():
    """Тест получения рецептов для станции"""
    system = create_all_recipes()
    
    # Разблокируем несколько рецептов
    system.unlock_recipe("wooden_stick")
    system.unlock_recipe("iron_sword")
    system.unlock_recipe("healing_potion_basic")
    
    # Получаем рецепты для верстака tier 1
    workbench_recipes = system.get_recipes_for_station("workbench", 1)
    assert len(workbench_recipes) == 1  # Только wooden_stick
    
    # Получаем рецепты для верстака tier 2
    workbench_recipes_t2 = system.get_recipes_for_station("workbench", 2)
    assert len(workbench_recipes_t2) == 2  # wooden_stick + iron_sword
    
    # Получаем рецепты для лаборатории
    lab_recipes = system.get_recipes_for_station("laboratory", 1)
    assert len(lab_recipes) == 1  # healing_potion_basic
    
    print("✅ test_get_recipes_for_station пройден")


def test_recipe_serialization():
    """Тест сериализации рецепта"""
    recipe = Recipe(
        id="test_recipe",
        name="Тестовый рецепт",
        description="Описание",
        category=RecipeCategory.TOOLS,
        required_station="workbench",
        ingredients={"wood": 2},
        result_item="test_item",
    )
    
    # Сериализуем
    data = recipe.to_dict()
    
    # Десериализуем
    restored = Recipe.from_dict(data)
    
    assert restored.id == recipe.id
    assert restored.category == recipe.category
    assert restored.ingredients == recipe.ingredients
    
    print("✅ test_recipe_serialization пройден")


def test_system_serialization():
    """Тест сериализации системы"""
    system = CraftingSystem()
    
    recipe = Recipe(
        id="test_item",
        name="Тестовый предмет",
        description="Описание",
        category=RecipeCategory.TOOLS,
        required_station="workbench",
        ingredients={"wood": 1},
        result_item="test_item",
    )
    
    system.add_recipe(recipe)
    system.unlock_recipe("test_item")
    
    # Сериализуем
    data = system.to_dict()
    
    # Десериализуем
    restored = CraftingSystem.from_dict(data)
    
    assert len(restored.recipes) == len(system.recipes)
    assert len(restored.unlocked_recipes) == len(system.unlocked_recipes)
    assert "test_item" in restored.unlocked_recipes
    
    print("✅ test_system_serialization пройден")


def test_all_preset_recipes():
    """Тест всех предустановленных рецептов"""
    system = create_all_recipes()
    
    # Проверяем, что рецепты созданы
    assert len(system.recipes) > 0
    
    # Проверяем рецепты верстака
    workbench_recipes = create_workbench_recipes()
    assert len(workbench_recipes) > 0
    
    # Проверяем рецепты лаборатории
    lab_recipes = create_laboratory_recipes()
    assert len(lab_recipes) > 0
    
    print("✅ test_all_preset_recipes пройден")


def run_all_tests():
    """Запустить все тесты"""
    print("\n🧪 Запуск тестов системы крафта...\n")
    
    test_recipe_creation()
    test_can_craft()
    test_crafting_system()
    test_craft_item_success()
    test_craft_item_not_unlocked()
    test_craft_with_quality_bonus()
    test_get_recipes_for_station()
    test_recipe_serialization()
    test_system_serialization()
    test_all_preset_recipes()
    
    print("\n✅ Все тесты пройдены успешно!\n")


if __name__ == "__main__":
    run_all_tests()
